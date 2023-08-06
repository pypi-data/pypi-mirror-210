import datetime
import json

import xarray as xr


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def add_time_dimension(dataset):
    """
    Collapse a 2D Xarray Dataset, with each band + date combination as a separate variable, into a 3D Xarray Dataset, with dimensions of x, y, and time.
    The current implementation assumes only bands with the name beginning with "s1" or "s2" have a time dimension. Bands not beginning with those strings (assumed to be custom rasters or vectors)
    are first dropped, then assigned to the final dataset with only x and y dimensions.
    """
    date_coo = []
    other_var = {}
    var_data = {}
    data_variables = {}

    if "spatial_ref" in list(dataset.data_vars.keys()):
        dataset = dataset.set_coords(("y", "x", "spatial_ref"))

    for key in dataset.data_vars.keys():
        if not (key.startswith("s2") or key.startswith("s1")):
            other_var[key] = (["y", "x"], dataset[key].to_numpy())
            dataset = dataset.drop(key)

    for key in dataset.data_vars.keys():
        if not (key[:-9] in var_data.keys()):
            var_data[key[:-9]] = []
        if not (datetime.datetime.strptime(key[-8:], "%Y%m%d") in date_coo):
            date_coo.append(datetime.datetime.strptime(key[-8:], "%Y%m%d"))
        var_data[key[:-9]].append(dataset[key].to_numpy())

    for param_nam in var_data.keys():
        data_variables[param_nam] = (["time", "y", "x"], var_data[param_nam])

    data_variables = {**data_variables, **other_var}

    ds = xr.Dataset(
        data_vars=data_variables, coords={"time": date_coo, "y": dataset.y, "x": dataset.x}, attrs=dataset.attrs
    )
    if "nodatavals" in ds.attrs:
        del ds.attrs["nodatavals"]
    if "scales" in ds.attrs:
        del ds.attrs["scales"]
    if "offsets" in ds.attrs:
        del ds.attrs["offsets"]
    if "descriptions" in ds.attrs:
        del ds.attrs["descriptions"]
    return ds


def remove_time_dimension(dataset):
    """
    Expand a 3D Xarray Dataset, with dimensions of x, y, and time, into a 2D Xarray Dataset, with band_name = band_name + date_without_separators.
    """
    if "spatial_ref" in list(dataset.data_vars.keys()):
        dataset = dataset.set_coords(("y", "x", "spatial_ref"))

    data_variables = {}
    variable_attributes = {}
    weath_dict = {}

    dates_ns64 = dataset.time.to_numpy()
    for key in dataset.data_vars.keys():
        # Iterate over each date inside the band
        if key.startswith("S1") or key.startswith("S2"):
            for date_ns64 in dates_ns64:
                # Convert date from datetime64 format to date string in%Y%m%d format
                ns = 1e-9
                date_in_datetime = datetime.datetime.utcfromtimestamp(date_ns64.astype(int) * ns)
                date_without_separators = date_in_datetime.strftime("%Y%m%d")
                new_key = key + "_" + date_without_separators
                sliced_dataset = dataset[key].sel(time=date_ns64)
                # If the band is not filled with nodata values, add it to the dataset
                if not check_if_all_elements_are_nan(sliced_dataset):
                    data_variables[new_key] = (["y", "x"], sliced_dataset.to_numpy())
                    if key.startswith("s1"):
                        # Copy attributes from the original band except for scene_metadata
                        if variable_attributes.get(new_key) is None:
                            variable_attributes[new_key] = reduce_attributes(dataset[key].attrs)
                        scene_metadata = eval(dataset[key].attrs["scene_metadata"])
                        if scene_metadata.get(date_in_datetime.isoformat()) is not None:
                            variable_attributes[new_key]["scene_metadata"] = json.dumps(
                                scene_metadata[date_in_datetime.isoformat()]
                            )
                        # add tifftag and date in attributes
                        variable_attributes[new_key]["TIFFTAG_DATETIME"] = date_in_datetime.date().isoformat()
                        variable_attributes[new_key]["date"] = date_in_datetime.date().isoformat()
                    else:
                        variable_attributes[new_key] = dataset[key].attrs
        elif key.startswith("WEATHER"):
            for date_ns64 in dates_ns64:
                ns = 1e-9
                date_in_datetime = datetime.datetime.utcfromtimestamp(date_ns64.astype(int) * ns)
                weath_dict[key + "_" + str(date_in_datetime.isoformat())] = dataset[key].sel(time=date_ns64)
        else:
            data_variables[key] = (["y", "x"], dataset[key].to_numpy())
            variable_attributes[key] = dataset[key].attrs

    ds = xr.Dataset(data_vars=data_variables, coords={"y": dataset.y, "x": dataset.x}, attrs=dataset.attrs)
    if weath_dict != {}:
        ds.attrs["WEATHER"] = weath_dict
    for var_name in ds.data_vars.keys():
        ds[var_name].attrs = variable_attributes.get(var_name)
    return ds


def check_if_all_elements_are_nan(array):
    """
    Check if all elements of an array are nan.
    """
    null_flag_array = array.isnull().to_numpy()
    return all(all(item == 1 for item in items) for items in null_flag_array)


def reduce_attributes(attributes):
    """
    Reduce the attributes of a dataset to a smaller set of attributes.
    """
    reduced_attributes = {}
    for key in attributes.keys():
        if key not in ["scene_metadata", "date", "TIFFTAG_DATETIME"]:
            reduced_attributes[key] = attributes[key]
    return reduced_attributes
