"""
core.py
====================================
All classes necessary to use SpaceSense library.
"""
import datetime
import json
import logging
import os
import uuid
from tempfile import NamedTemporaryFile
from typing import Any, List, Union

import grpc
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Struct
from pandas.core.frame import DataFrame
from rasterio.io import MemoryFile
from satstac import Collection, Item, ItemCollection
from xarray.core.dataset import Dataset

from spacesense import config, utils
from spacesense.collections.models import Sentinel1SearchResult, Sentinel2SearchResult, WeatherSearchResult
from spacesense.common.proto.backend import backend_pb2
from spacesense.file_handler import Raster, Vector
from spacesense.grpc_client import GrpcClient
from spacesense.job import Job, JobList

logger = logging.getLogger(__name__)


class Sentinel1ResultItem:
    """Class representing one result item from :py:meth:`Client.compute_ard`"""

    def __init__(self, date, status, data=None, reason=None, file_path=None, bucket_path=None):
        """Create an instance of the :py:class:`Client.Sentinel1ResultItem`"""
        self.date = date
        self.status = status
        self.scene_metadata = None
        self._data = data
        self.file_path = file_path
        self.reason = reason
        self.bucket_path = bucket_path
        self.data = None
        if self.file_path:
            self._init_from_local_file()
        elif self._data and len(self._data) > 0:
            with MemoryFile(self._data) as mem_file:
                # xr.open_rasterio is deprecated
                # but we can't use xr.open_dataset(mem_file.name, engine="rasterio") or rio.open_rasterio(os.path.join(user_files[0].file_path))
                # because currently we lose the geotiff "scene_metadata"
                data_array = xr.open_rasterio(mem_file.name)
                self.data = self._redesign_to_dataset(data_array)

    def _init_from_local_file(self):
        # xr.open_rasterio is deprecated
        # but we can't use xr.open_dataset(mem_file.name, engine="rasterio") or rio.open_rasterio(os.path.join(user_files[0].file_path))
        # because currently we lose the geotiff "scene_metadata"
        data_array = xr.open_rasterio(self.file_path)
        # init date
        self.date = datetime.datetime.strptime(data_array.attrs["TIFFTAG_DATETIME"], "%Y:%m:%d %H:%M:%S")

        # init scene metadata
        scene_metadata_list = list(eval(data_array.attrs["scene_metadata"]))
        scene_metadata_with_date = []
        for scene_metadata in scene_metadata_list:
            scene_metadata_copy = {"date": self.date}
            scene_metadata_copy.update(scene_metadata)
            scene_metadata_with_date.append(scene_metadata_copy)
        self.scene_metadata = scene_metadata_with_date

        # redesign dataset to
        self.data = self._redesign_to_dataset(data_array)

    def _redesign_to_dataset(self, data_array: xr.DataArray) -> Dataset:
        """Reformat the metadata from the geotiff to a dict"""
        data_array.attrs["scene_metadata"] = self.scene_metadata
        data_array.coords["time"] = self.date
        # Create a dataset by splitting bands into separate variables
        dataset = data_array.to_dataset(dim="band", promote_attrs=True)
        # Rename data variables into more relevant name
        dataset = dataset.rename_vars({1: "vh", 2: "vv", 3: "lia", 4: "mask"})
        return dataset

    def __str__(self):
        """Returns a formated representation of the result Item"""
        return f"date={self.date}, status={self.status}, file_path={self.file_path}"

    @property
    def processing_status(self) -> dict:
        """Returns information about the processing status"""
        return {
            "date": self.date,
            "status": self.status,
            "reason": self.reason,
            "file_path": self.file_path,
        }


class Sentinel1Result:
    """Class containing the result of :py:meth:`Client.compute_ard`

    Attributes:
        ok (bool): :py:attr:`Sentinel1Result.ok` is True when :py:meth:`Client.compute_ard` returns usable data, False otherwise.
        reason (str, None): Provides additional information when :py:attr:`Sentinel1Result.ok` is false and result is not accessible. if :py:attr:`Sentinel1Result.ok` is True, :py:attr:`Sentinel1Result.reason` will be None.
        items (list): List contraining :py:class:`Sentinel1ResultItem`
    """

    def __init__(self, items: List[Sentinel1ResultItem] = None, ok=True, reason=None):
        self.ok: bool = ok
        self.reason: str = reason
        self._items = items if items is not None else []
        self._items.sort(key=lambda x: x.date)
        self._scene_metadata = None
        self._dataset = None
        self._status = None

    @property
    def status(self) -> DataFrame:
        """Returns the status for each scene as a DataFrame

        Returns:
            DataFrame containing the status for each scene.

        Raise:
            RuntimeError: Result not OK. when :py:attr:`Sentinel1Result.ok` is False
        """
        if self.ok is False and self.reason:
            raise RuntimeError(f"S1 result not ok: {self.reason}")
        if self._status is None:
            self._compute_status()
        return self._status

    @property
    def dataset(self) -> Dataset:
        """Returns a Dataset containing all the Items.

        Returns:
            Dataset containing all the Items.

        Raise:
            RuntimeError: Result not OK. when :py:attr:`Sentinel1Result.ok` is False
        """
        if not self.ok:
            raise RuntimeError("Result not OK")
        if not self._dataset:
            self._compute_dataset()
        return self._dataset

    def _compute_dataset(self):
        self._dataset = xr.concat([item.data for item in self._items], dim="time").sortby("time")

    def _compute_status(self):
        self._status = pd.DataFrame.from_dict([item.processing_status for item in self._items], orient="columns")

    @property
    def scene_metadata(self) -> pd.DataFrame:
        """Returns the metadata for each scene as a Dataframe

        Args:
            returns the scene metadata.

        Returns:
            pd.DataFrame containing the scene metadata as dictionary for each available scenes.
        """
        if not self._scene_metadata:
            scene_metadata_with_date = []
            for item in self._items:
                date_metadata = item.scene_metadata
                scene_metadata_with_date.extend(iter(date_metadata))
            self._scene_metadata = pd.DataFrame.from_dict(scene_metadata_with_date, orient="columns")
        return self._scene_metadata


class FuseResult:
    """Class containing the result of :py:meth:`Client.fuse`

    Attributes:
        ok: Status output of the fusion, True indicates a valid return of the fused result
        reason: Description of the 'ok' status
        file_path: Directory path to the saved result
        fuse_id: Unique ID generated by the fusion process, can be used in file naming
        dataset (Xarray Dataset): The fusion result returned as a 3 dimensional (x, y, and time) Xarray Dataset containing all fused data layers and attributes
            properties (described below)

    The `Xarray Dataset <https://docs.xarray.dev/en/stable/getting-started-guide/why-xarray.html>`_ created is a multi-dimensional array allowing for detailed encoding of
    the included information. Information such as time, geolocation, and the additional information and metadata needed to fully know what the information is that you are
    handelling. Finally, Xarray provides a powerful selection and processing interface allowing you to take the result of your data fusion, and transform it to your specific needs.

    Example
    ---------
    >>> result = client.fuse(catalogs_list = [s1_search_result, s2_search_result, weather_search_result],
                             to_fuse = [custom_raster, custom_vector],
                             )
    >>> result.dataset
    """

    def __init__(
        self, ok=True, reason=None, status=None, data=None, file_path=None, base_dir=None, client_id=None, fuse_id=None
    ):
        self.ok: bool = ok
        self.reason: str = reason
        self.status = status
        self._data = data
        self.file_path = file_path
        self.base_dir = base_dir
        self.client_id = client_id
        self.fuse_id = fuse_id
        self.output_dir = os.path.join(self.base_dir, self.client_id) or file_path
        self.filename = self.fuse_id if self.fuse_id else self.client_id
        self._nc_path = os.path.join(self.output_dir, self.filename + ".nc")
        self._geotiff_path = os.path.join(self.output_dir, self.filename + ".tif")

        if self.file_path:
            self._init_from_local_file()
        elif self._data and len(self._data) > 0:
            with NamedTemporaryFile(suffix=".nc") as tempfile:
                tempfile.write(self._data)
                dataset = xr.open_dataset(tempfile.name, decode_coords="all", engine="netcdf4", mask_and_scale=False)
                if dataset.attrs.get("additional_info"):
                    dataset.attrs["additional_info"] = eval(dataset.attrs["additional_info"])
            self._dataset = dataset

    @property
    def dataset(self):
        if self.ok is False and self.reason:
            raise RuntimeError(f"Fuse result not ok: {self.reason}")
        else:
            return self._dataset

    def _init_from_local_file(self):
        with xr.open_dataset(self.file_path, decode_coords="all", engine="netcdf4", mask_and_scale=False) as ds:
            dataset = ds.load()
        if dataset.attrs.get("additional_info"):
            dataset.attrs["additional_info"] = eval(dataset.attrs["additional_info"])
        self._dataset = dataset

    def __str__(self):
        """Returns a formated representation of the result Item"""
        return f"ok={self.ok}, status={self.status}, data={len(self.data)}, file_path={self.file_path}"

    def to_geotiff(self, file_path: str = None):
        """Save the result to a `geotiff file <https://www.earthdata.nasa.gov/esdis/esco/standards-and-references/geotiff>`_

        Parameters:
            file_path: Path to target save directory

        """
        # Save to geotiff
        if file_path is None:
            file_path = self._geotiff_path
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        ds = utils.remove_time_dimension(self.dataset)
        ds.rio.to_raster(file_path)
        return file_path

    def to_netcdf(self, file_path: str = None):
        """Save the result to a `netcdf file <https://www.unidata.ucar.edu/software/netcdf/>`_

        Parameters:
            file_path: Path to target save directory
        """
        # Save to netcdf
        if file_path is None:
            file_path = self._nc_path
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        if self.dataset.attrs.get("additional_info"):
            self.dataset.attrs["additional_info"] = json.dumps(self.dataset.attrs.get("additional_info"))
            self.dataset.to_netcdf(file_path)
            self.dataset.attrs["additional_info"] = eval(self.dataset.attrs["additional_info"])
        else:
            self.dataset.to_netcdf(file_path)
        return file_path

    def plot_rgb(
        self,
        all_dates=True,
        brightness_factor: float = 1,
        date: str = None,
        figsize: list = [8, 6],
        aspect: str = "auto",
        save: bool = False,
        save_dir: str = "./figures",
    ):
        """Creates an RGB image of the dataset. The red, green, and blue bands are automatically detected, normalized, stacked, and displayed for each date (by default)
        that there is a Sentinel-2 image.

        Parameters:
            all_dates (bool): Boolean to plot all dates. If False, only the first date with an S2 image will be plotted
            brightness_factor (float): Float to scale the brightness of the image. Values above 1 may be useful for viewing normally dark images
            date (str): String in "YYYY-MM-DD" format to select and plot only a specific date in the fused dataset
            figsize (list): X and Y size parameters for figure size. Only applicable if all_dates = False or a date is specified
            aspect (str): `Matplotlib aspect ratio parameter <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_aspect.html>_`. Sets the aspect ratio of the axes (y/x) scaling. "auto" fills the position rectangle with data. "equal" creates the same scaling from data to plot units for x and y.
            save (bool): Option to save figure.
            save_dir (str): Directory path of where to save the figure if save is set to True.
        """

        # Define normalization function to call for RGB plotting
        def norm(band):
            band_min, band_max = band.min(), band.max()
            return (band - band_min) / (band_max - band_min)

        # Set up a dataset with only Bands 2, 3, and 4, and only times when S2 data is present
        ds = self.dataset
        S2_count = 0
        dates = []
        ncols = 2
        var_names = ["S2_BLUE", "S2_GREEN", "S2_RED"]
        band_names = ["S2_B02", "S2_B03", "S2_B04"]
        for elem in var_names:
            if elem in ds.data_vars:
                if elem == "S2_BLUE":
                    ds = ds.rename_vars({"S2_BLUE": "S2_B02"})
                elif elem == "S2_GREEN":
                    ds = ds.rename_vars({"S2_GREEN": "S2_B03"})
                elif elem == "S2_RED":
                    ds = ds.rename_vars({"S2_RED": "S2_B04"})

        if not all(x in ds.data_vars for x in band_names):
            logger.info(
                'One or several required bands are not present. Please pass a dataset with "S2_B02","S2_B03", and "S2_B04" or "S2_BLUE","S2_GREEN", and "S2_RED".'
            )
            return

        if date:
            dates.append(date)
            S2_count = 1
            ncols = 1
            all_dates = False
        else:
            for i, time in enumerate(ds.time):
                ds_i = ds.isel(time=i)
                if not np.isnan(ds_i.S2_B02.mean()):
                    S2_count += 1
                    dates.append(ds_i.time.dt.date.values.astype(str))

        ds_s2 = ds[band_names].sel(time=dates)
        nrows = int((S2_count + 1) / 2)

        # If plotting all dates, run through the S2 dataset, else pick only the first date
        if all_dates is True and len(dates) > 1:
            fig, axs = plt.subplots(nrows=nrows, ncols=ncols, figsize=(ncols * 8, nrows * 6))
            for i, time in enumerate(ds_s2.time):
                ds_i = ds_s2.isel(time=i)

                blue = norm(ds_i.S2_B02) * brightness_factor
                green = norm(ds_i.S2_B03) * brightness_factor
                red = norm(ds_i.S2_B04) * brightness_factor
                rgb = np.dstack([red, green, blue])

                ax = fig.axes[i]
                ax.set_title(ds_i.time.dt.date.values.astype(str))
                ax.axis("off")
                ax.imshow(rgb, aspect=aspect)
        else:
            fig, axs = plt.subplots(nrows=1, ncols=1, figsize=(figsize[0], figsize[1]))
            ds_i = ds_s2.isel(time=0)

            blue = norm(ds_i.S2_B02) * brightness_factor
            green = norm(ds_i.S2_B03) * brightness_factor
            red = norm(ds_i.S2_B04) * brightness_factor
            rgb = np.dstack([red, green, blue])

            ax = fig.axes[0]
            ax.set_title(ds_i.time.dt.date.values.astype(str))
            ax.axis("off")
            ax.imshow(rgb, aspect=aspect)
        if save is True:
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            fig.savefig(fname=save_dir + "/plot_rgb.png", bbox_inches="tight")

    def plot_timeseries(self, variables: list = None, save: bool = False, save_dir: str = "./figures"):
        """
        Creates a normalized time series of the provided list of variables in the dataset. By default, all variables in the fused dataset are plotted.
        The time series is created by taking the spatial average at each time for each variable. Then, those values are converted into normalied values and plotted.

        Parameters:
            variables (list): List of data variable names in the fuseResult dataset to graph in a time series plot
            save (bool): Option to save figure.
            save_dir (str): Directory path of where to save the figure if save is set to True.
        """

        def norm(band):
            band_min, band_max = band.min(), band.max()
            return (band - band_min) / (band_max - band_min)

        colors = [
            "r",
            "g",
            "b",
            "c",
            "m",
            "y",
            "k",
            "olive",
            "gray",
            "pink",
            "brown",
            "orange",
            "lightgreen",
            "gold",
            "turquoise",
            "navy",
            "maroon",
            "darkviolet",
            "indigo",
            "wheat",
        ]
        variables = variables or list(self.dataset.data_vars)
        ds = self.dataset
        fig, axs = plt.subplots(figsize=(10, 5))
        for i, var in enumerate(variables):
            if "x" in ds[var].coords:
                n = norm(ds[var].mean(dim={"y", "x"}))
                y = n.dropna(dim="time")
                x = n.dropna(dim="time").time
                axs.plot(x, y, linestyle="-", label=var, color=colors[i])
            else:
                n = norm(ds[var])
                y = n.dropna(dim="time")
                x = n.dropna(dim="time").time
                axs.plot(x, y, linestyle="--", label=var, color=colors[i])

        axs.set_ylabel("Normalized Magnitude")
        axs.set_xlabel("Date")
        axs.tick_params(axis="x", rotation=45)
        axs.legend(loc="upper center", bbox_to_anchor=(0.5, -0.25), fancybox=True, shadow=True, ncol=5)
        if save is True:
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            fig.savefig(fname=save_dir + "/plot_timeseries.png", bbox_inches="tight")

    def plot_availability(
        self, tick_spacing: int = 1, advanced: str = False, save: bool = False, save_dir: str = "./figures"
    ):
        """
        Creates a block time series of each variable type (Sentinel-1, Sentinel-2, or Weather) in the dataset for each date. Times with white color indicate no data was available for that variable on that date.
        In normal mode, blocks with dark blue color indicate data availability. In advanced mode, blocks with any color other than white indicate data availability.

        Parameters:
            tick_spacing (int): Integer value to indicate the x axis (time) tick interval when plotting the dataset. A 2 indicates that every 2 dates show up as a tick
            and is labeled.
            advanced (bool): Boolean to enable advanced plot mode. The advanced plot expands all sensors (S1, S2, and Weather) into individual bands, as well as plotting a normalized
            magnitude value as the color, instead of a simple binary "present" or "not present".
            save (bool): Option to save figure.
            save_dir (str): Directory path of where to save the figure if save is set to True.
        """

        def norm(band):
            band_min, band_max = band.min(), band.max()
            return (band - band_min) / (band_max - band_min)

        ds = self.dataset
        times = pd.to_datetime(ds.time.dt.date)

        if advanced is False:
            vars = []
            for i, v in enumerate(ds.data_vars):
                if "S1" in v and "S1" not in vars:
                    vars.append("S1")
                elif "S2" in v and "S2" not in vars:
                    vars.append("S2")
                elif "WEATHER" in v and "WEATHER" not in vars:
                    vars.append("WEATHER")
            avail = pd.DataFrame(index=times, columns=vars)
            for i, var in enumerate(ds.data_vars):
                for t, time in enumerate(ds.time):
                    data = ds[var].isel(time=t)
                    if not np.isnan(data.mean()):
                        if "S1" in var:
                            avail.at[time.values, "S1"] = 1
                        if "S2" in var:
                            avail.at[time.values, "S2"] = 1
                        if "WEATHER" in var:
                            avail.at[time.values, "WEATHER"] = 1

            fig, axs = plt.subplots(figsize=(10, 0.15 * len(var)))
            avail = avail.astype(float)

            axs.set_yticks(np.arange(0.5, len(avail.columns)), avail.columns)
            axs.set_xticks(np.arange(0, len(avail.index))[0::tick_spacing], labels=avail.index.date[0::tick_spacing])

            plt.setp(axs.get_xticklabels(), rotation=30, ha="right")
            plt.pcolor(avail.T, edgecolors="k", linewidths=2, cmap="plasma")

            axs.set_ylabel("Variables")
            axs.set_xlabel("Dates")

        elif advanced is True:
            fig, axs = plt.subplots(figsize=(10, 5))
            vars = [i for i in ds.data_vars]
            avail = pd.DataFrame(index=times, columns=vars)
            for i, var in enumerate(ds.data_vars):
                for t, time in enumerate(ds.time):
                    n = norm(ds[var])
                    data = ds[var].isel(time=t)
                    if not np.isnan(data.mean()):
                        avail.at[time.values, var] = n.isel(time=t).mean().values
                    else:
                        avail.at[time.values, var] = np.nan

            avail = avail.astype(float)

            axs.set_yticks(np.arange(0.5, len(avail.columns)), avail.columns)
            axs.set_xticks(np.arange(0, len(avail.index))[0::tick_spacing], labels=avail.index.date[0::tick_spacing])

            plt.setp(axs.get_xticklabels(), rotation=30, ha="right")
            plt.pcolor(avail.T, edgecolors="k", linewidths=2, cmap="plasma")
            cbar = plt.colorbar()
            cbar.set_label("Normalized Magnitude", rotation=270)
            axs.set_ylabel("Variables")
            axs.set_xlabel("Dates")

        if save is True:
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            fig.savefig(fname=save_dir + "/plot_availability.png", bbox_inches="tight")


class Client:
    """Class that allows you to interact with SpaceSense backend. This is the access point to the major SpaceSense processes such as
    searching for satellite and catalog scenes and data fusion. You can interact with this class to change the result options, such as CRS, resolution, and if and where
    to save the result."""

    def __init__(self, id=None, backend_url=None, api_key=None):
        """Create an instance of the :py:class:`Client`

        Args:
            id (str, optional): Unique id of your client instance used to organize results and track usage. If not specified, automatically generates a unique ID
            backend_url (str, optional): For development purposes only

        """
        backend_url = backend_url or config.BACKEND_URL
        if api_key:
            logger.warning(
                """Be careful not to push your API key to a public repository.
                It is recommended to use the SS_API_KEY environment variable instead of passing the key directly to the Client."""
            )
        api_key = api_key or os.environ.get("SS_API_KEY")
        if not api_key:
            raise ValueError("Could not find SpaceSense API in SS_API_KEY environment variable.")

        grpc_client = GrpcClient()
        grpc_client.initialize(api_key, backend_url)
        self.core_stub = grpc_client.core_stub
        self.job_stub = grpc_client.job_stub
        self.id = id or str(uuid.uuid4())
        self.local_output_path = "./generated"
        self.save_to_local = False
        self.save_to_bucket = False
        self.output_crs = None
        self.output_resolution = None

    def set_output_crs(self, output_crs):
        """Set the desired output CRS.

        Args:
            output_crs (int): Desired output CRS number.
                Default: ``'4326'``

        Set :py:attr:`self.output_crs` to a specified `EPSG code`_ as an int.
        :py:attr:`self.output_crs` will define the EPSG of the output returned by :py:meth:`Client.compute_ard` and :py:meth:`Client.fuse`

        .. _EPSG code:
            https://epsg.io/
        """
        self.output_crs = output_crs

    def set_output_resolution(self, resolution):
        """Set the desired output pixel size (resolution).

        Args:
            resolution (int): desired output resolution.

        Set :py:attr:`self.output_resolution` to a specified output resolution in meters²/pixel. Default value is 10m²/pixel.
        :py:attr:`self.output_resolution` will define the resolution of the output returned by :py:meth:`Client.fuse`

        .. csv-table::
            :header: Catalog Data, Type, Description, Native Resolution

            Sentinel-1, Satellite (SAR), Sentinel-1 Interferometric Wide swath (IW) mode of level 1 Ground Range Detected (GRD) data, 10m²/pixel
            Sentinel-2, Satellite (Optical and NIR), Level 2A atmospherically corrected data, 10m²/pixel

        Please keep these native resolution in mind when up or downscaling the output resolution.

        """
        self.output_resolution = resolution

    def _enable_bucket_output(self, bucket_output_path):
        """Enables the save to bucket option.

        Sets :py:attr:`self.save_to_bucket` to True
        and sets :py:attr:`self.bucket_output_path` to the specified bucket path string.
        The output of compute_ard will be saved in the specified bucket.

        Args:
            bucket_output_path (str): Public bucket path,
        Note:
            the :py:attr:`self.bucket_output_path` should be a valid bucket path as a string. it should be accessible in order for the data to be saved.

        """
        self.save_to_bucket = True
        self.bucket_output_path = bucket_output_path

    def _disable_bucket_output(self):
        """Disables the save to bucket option.

        Sets :py:attr:`self.save_to_bucket` to False
        The output will no longer be saved in the specified bucket
        """
        self.save_to_bucket = False

    def enable_local_output(self, local_output_path="./generated"):
        """Enables the local output option. Saves the fused result to a netCDF file in the ./generated folder with the client ID
        as a sub-directory.

        Args:
            local_output_path (str): path to local directory.

        Sets :py:attr:`self.save_to_local` to True
        and sets :py:attr:`self.local_output_path` to the desired local output path string.
        The output will be saved in the specified directory.

        """
        self.save_to_local = True
        self.local_output_path = local_output_path

    def disable_local_output(self):
        """Disables the local output option.

        Sets :py:attr:`self.save_to_local` to False
        The output will no longer be saved in the specified local directory.

        """
        self.save_to_local = False

    def s1_search(self, aoi, start_date, end_date, query_filters=dict(), data_coverage=100) -> Sentinel1SearchResult:
        """
        Search for Sentinel-1 scenes in a given area of interest. Currently, single AOIs are limited to a total size of 250km\\ :sup:`2` or smaller.

        Parameters:
            aoi (geojson): A GeoJSON polygon
            start_date (str or datetime): Start date of the search
            end_date (str or datetime): End date of the search
            query_filters (dict, optional): Filters to apply to the search query
            data_coverage (int, optional): Minimum percent of the AOI covered by valid (i.e. non NaN) S1 data

        :rtype: :py:class:`models.Sentinel1SearchResult`

        :return: :py:class:`models.Sentinel1SearchResult` object, continaing a pandas dataframe with the resulting S1 scenes from the search

        The following S1 scene parameters are usable in the query_filter parameter:

            - orbitdirection
            - relativeorbitnumber
            - lastrelativeorbitnumber
            - orbitnumber
            - lastorbitnumber
            - polarizationmode

        .. note:: s1_search by default returns **ALL** S1 scenes meeting the date and query_filter parameters. This means there can be single dates with more than one S1 observation in the search result (e.g. overlapping tiles). As mosaicing is not yet supported, only a single observation per date is currently allowed by the fuse function, so one can use the "filter_duplicate_dates" function of the search result to automatically take the observation with the best coverage.

        .. warning::
            The duration of the search is limited in this interactive search mode. Searching for more than 2 years of Sentinel-1 or Sentinel-2 data in a single "s1_search" or "s2_search"
            may result in errors or non-response from our backend.

            If you wish to search for more than 2 years, we recommend using multiple, ideally yearly, searches and concatenating them with the :py:meth:`models.Sentinel1SearchResult.concat` or
            :py:meth:`models.Sentinel2SearchResult.concat` methods.

            SpaceSense considers it best practice to use 1 year as the maximum search duration.

        Example
        ----------
            >>> query_filters = {"orbitdirection" : "DESCENDING", "lastrelativeorbitnumber" : "52"}
            >>> client.s1_search(aoi = aoi,
                                 start_date = start_date,
                                 end_date = end_date,
                                 query_filters = query_filters)

        For more examples, please see the `Search S1 and S2 <../notebooks/2_search_s1_s2.html>`_ and `Search and filter S1 and S2 data <../notebooks/3_filter_s1_s2.html>`_.

        """

        aoi_param = Struct()
        aoi_param.update(aoi)

        if type(start_date) == str:
            start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()

        if type(start_date) != datetime.date:
            raise ValueError("Invalid start_date, should be a datetime.date object or a str in isoformat")

        if type(end_date) == str:
            end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()

        if type(end_date) != datetime.date:
            raise ValueError("Invalid end_date, should be a datetime.date object or a str in isoformat")

        if start_date == end_date:
            end_date = end_date + datetime.timedelta(days=1)
            logger.warning("start_date and end_date are the same, adding 1 day to end_date")

        query_filter_struct = Struct()
        if query_filters is not None:
            query_filter_struct.update(query_filters)

        filtering_options = Struct()
        filtering_options.update({"data_coverage": data_coverage})

        try:
            response = self.core_stub.GetS1Search(
                backend_pb2.GetS1SearchRequest(
                    experiment_id=self.id,
                    aoi=aoi_param,
                    start_date=start_date.isoformat(),
                    end_date=end_date.isoformat(),
                    sentinel_filtering_options=query_filter_struct,
                    filtering_options=filtering_options,
                )
            )
            scene_list = _extract_scenes(response.scenes)
            return Sentinel1SearchResult(aoi, data_coverage, scene_list)
        except grpc.RpcError as e:
            logger.error(e.details())
            return Sentinel1SearchResult(aoi, data_coverage=None, scenes=None, ok=False, reason=e.details())

    def s2_search(self, aoi, start_date, end_date, query_filters=None) -> Sentinel2SearchResult:
        """
        Search for Sentinel-2 scenes in a given area of interest. Currently, single AOIs are limited to a total size of 250km\\ :sup:`2` or smaller.

        Parameters:
            aoi (geojson): A GeoJSON polygon
            start_date (str or datetime): Start date of the search
            end_date (str or datetime): End date of the search
            query_filters (dict, optional): Filters to apply to the search query

        :rtype: :py:class:`models.Sentinel2SearchResult`

        :return: :py:class:`models.Sentinel2SearchResult` object, continaing a pandas dataframe with the resulting S2 scenes from the search

        The following S2 scene parameters are usable in the query_filter parameter:

            - valid_pixel_percentage
            - swath_coverage_percentage
            - no_data
            - cloud_shadows
            - vegetation
            - not_vegetated
            - water
            - cloud_medium_probability
            - cloud_high_probability
            - thin_cirrus
            - snow

        .. note:: s2_search by default returns **ALL** S2 scenes meeting the date and query_filter parameters. This means there can be single dates with more than one S2 observation in the search result (e.g. overlapping tiles). As mosaicing is not yet supported, only a single observation per date is currently allowed by the fuse function, so one can use the "filter_duplicate_dates" function of the search result to automatically take the observation with the best coverage.

        .. warning::
            The duration of the search is limited in this interactive search mode. Searching for more than 2 years of Sentinel-1 or Sentinel-2 data in a single "s1_search" or "s2_search"
            may result in errors or non-response from our backend.

            If you wish to search for more than 2 years, we recommend using multiple, ideally yearly, searches and concatenating them with the :py:meth:`models.Sentinel1SearchResult.concat` or
            :py:meth:`models.Sentinel2SearchResult.concat` methods.

            SpaceSense considers it best practice to use 1 year as the maximum search duration.

        Example
        ----------
            >>> query_filters = {"valid_pixel_percentage" : {">=": 50}, "cloud_medium_probability" : {"<=": 50}})
            >>> res_S2 = client.s2_search(aoi = aoi,
                                          start_date = start_date,
                                          end_date = end_date,
                                          query_filters = query_filters)

        For more examples, please see the `Search S1 and S2 <../notebooks/2_search_s1_s2.html>`_ and `Search and filter S1 and S2 data <../notebooks/3_filter_s1_s2.html>`_.

        """

        aoi_param = Struct()
        aoi_param.update(aoi)

        if type(start_date) == str:
            start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()

        if type(start_date) != datetime.date:
            raise ValueError("Invalid start_date, should be a datetime.date object or a str in isoformat")

        if type(end_date) == str:
            end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()

        if type(end_date) != datetime.date:
            raise ValueError("Invalid end_date, should be a datetime.date object or a str in isoformat")

        if start_date == end_date:
            end_date = end_date + datetime.timedelta(days=1)
            logger.warning("start_date and end_date are the same, adding 1 day to end_date")

        filters_param = Struct()
        if query_filters is not None:
            filters_param.update(query_filters)

        try:
            response = self.core_stub.GetS2Search(
                backend_pb2.GetS2SearchRequest(
                    experiment_id=self.id,
                    aoi=aoi_param,
                    start_date=start_date.isoformat(),
                    end_date=end_date.isoformat(),
                    filters=filters_param,
                )
            )

            geojson = json_format.MessageToDict(response.scenes)
            item_list = [Item(feature) for feature in geojson["features"]]
            collection_list = [Collection(collection) for collection in geojson["collections"]]
            item_collection = ItemCollection(items=item_list, collections=collection_list)
            return Sentinel2SearchResult(aoi, item_collection=item_collection)
        except grpc.RpcError as e:
            logger.error(e.details())
            return Sentinel2SearchResult(aoi, item_collection=None, ok=False, reason=e.details())

    def fuse(
        self,
        catalogs_list: List[Union[Sentinel1SearchResult, Sentinel2SearchResult, WeatherSearchResult]],
        fuse_id: str = None,
        aoi: Any = None,
        to_fuse: List[Union[Raster, Vector]] = [],
        additional_info: dict = None,
        output_resolution: int = None,
        output_crs: int = None,
    ) -> FuseResult:
        """Fuses catalog search results with any provided georeferenced raster and/or vector files.

        If only one catalog data type (Sentinel-1 or Sentinel-2) and no custom raster or vector files are provided, the fusion simply obtains and temporally fuses the satellite data.

        In general, fusion applies the following steps:
            - Reproject all data to the same CRS (if different)
            - Rasterize any vector objects
            - Clip all data to the same extent
            - Resample all data to the same pixel size
            - Co-register all data to the same grid
            - Stack all data into a single, time-enabled object

        In order to change the behavior of this method you can use other methods of :py:class:`Client`.

        .. note:: Resampling is performed using a `nearest neighbor resampling <https://catalyst.earth/catalyst-system-files/help/concepts/oraclegeomatica_c/oraclegeomatica3N118.html#:~:text=Nearest%20Neighbor%20(NN)%20resampling%20is,neighbor%20in%20the%20original%20raster>`__ technique. For this initial version, there is no way to change the resampling type, however this feature is coming soon.

        Parameters:
            catalogs_list (List[Union[Sentinel1SearchResult, Sentinel2SearchResult]]): List containing catalog search result objects.
            to_fuse (List[Union[Raster, Vector]]): List containing Raster and/or Vector objects.
            aoi (Any): Geojson feature or feature collection dictionary containing a polygon, overriding AOI provided in search result objects.
            additional_info (dict): Dictionary containing any additional information to fuse into the resulting attributes.
            output_resolution (int): Pixel size desired for all layers of the fused object, overriding client resolution.
            output_crs (int): CRS in EPSG format desired for all layers of the fused object, overriding client CRS.
            fuse_id (str): Numeric identifier of the fuse process.

        :rtype: :py:class:`FuseResult`

        Raise:
            ValueError: input is invalid.



        Example
        ----------
            >>> client = Client()
            >>> # Change the output CRS
            >>> client.set_output_crs(3857)
            >>> # Change the output resolution
            >>> client.set_output_resolution(8)
            >>> # Enable saving the result to a local file
            >>> client.enable_local_output()
            >>> # Fused data will be in CRS 3857 and
            >>> # at a resolution of 8 meters²/pixel
            >>> # Results will be saved at the default "./generated" directory
            >>> output = client.fuse([S1_search_results, S2_search_results])

        """
        output_resolution = output_resolution or self.output_resolution or None
        output_crs = output_crs or self.output_crs or None
        output_dir = os.path.join(self.local_output_path, self.id)

        params = Struct()
        if additional_info is not None:
            params.update({"additional_info": additional_info})

        if catalogs_list:
            satellite_list = [catalog for i, catalog in enumerate(catalogs_list) if catalog.NAME != "weather"]
        else:
            satellite_list = None

        if not satellite_list:
            raise ValueError("You need at least one Sentinel1SearchResult() or one Sentinel2SearchResult()")
        elif has_duplicates(satellite_list):
            raise ValueError(
                f"Got multiple catalogs of the same type '{type(has_duplicates(satellite_list))}'. expected a maximum of one for each catalog type"
            )
        elif has_empty_dataframe(satellite_list):
            raise ValueError(f"{type(has_empty_dataframe(satellite_list))}.dataframe is empty")

        catalogs_dict = {}
        # The structure of the dict should be :
        # catalogs_dict = {
        #     "s1": {"bands": [], "query_results": <List[dist]>, "sequence_index": 0},
        #     "s2": {"bands": [], "query_results": <ItemCollection>, "sequence_index": 1},
        #     "weather": {"data": [], "info":[], "sequence_index":1 or 2}
        # }
        for idx, catalog in enumerate(catalogs_list):
            catalogs_dict[catalog.NAME] = catalog.grpc_message
            catalogs_dict[catalog.NAME]["sequence_index"] = idx

        # search includes Weather as well here
        search_results_struct = Struct()
        search_results_struct.update(catalogs_dict)

        aoi_param = Struct()
        if aoi:
            aoi_param.update(aoi)
        else:
            aoi_param.update(catalogs_list[0].aoi)

        output_options = Struct()
        output_options.update(
            {
                "save_to_bucket": False,
                "save_to_file": False,
                "crs": output_crs,
                "resolution": output_resolution,
            }
        )

        request = backend_pb2.FuseRequest(
            experiment_id=self.id,
            aoi=aoi_param,
            params=params,
            output_options=output_options,
            search_results=search_results_struct,
        )
        # load raster and vector files
        for file_iterator in to_fuse:
            file_iterator.add_to_request(request)

        try:
            response = self.core_stub.Fuse(request)
            if response.status != "success":
                logger.info("failed")
                return FuseResult(
                    ok=False,
                    reason=response.reason,
                    status=response.status,
                    base_dir=self.local_output_path,
                    client_id=self.id,
                    fuse_id=fuse_id,
                )

            filename = fuse_id if fuse_id else self.id
            if not self.save_to_local:
                return FuseResult(
                    ok=True,
                    reason=response.reason,
                    status=response.status,
                    data=response.data,
                    base_dir=self.local_output_path,
                    client_id=self.id,
                    fuse_id=fuse_id,
                )

            file_path = os.path.join(output_dir, f"{filename}.nc")
            os.makedirs(output_dir, exist_ok=True)
            with open(file_path, "wb") as file:
                file.write(response.data)
            result = FuseResult(
                ok=True,
                reason=response.reason,
                status=response.status,
                file_path=file_path,
                base_dir=self.local_output_path,
                client_id=self.id,
                fuse_id=fuse_id,
            )
            logger.info("created everything")
            return result
        except grpc.RpcError as e:
            logger.error(e.details())
            return FuseResult(
                ok=False,
                reason=e.details(),
                base_dir=self.local_output_path,
                client_id=self.id,
                fuse_id=fuse_id,
            )

    def get_job(self, id: str, experiment_id: str = None):
        """Load a job from its id.

        Specifying an experiment id is optional, but recommended,

        if you are not using the same experiment id as the one used to start the job. you will need to specify the experiment id used for the job

        Args:
            id: ID generated when starting a job,
            experiment_id (str): ID of the experiment
        Returns:
            :py:class:`Job`
        """
        experiment_id = experiment_id or self.id
        return Job.load_from_id(
            id=id,
            experiment_id=experiment_id,
            job_stub=self.job_stub,
        )

    def get_job_list(self, experiment_id: str = None, workflow_id: str = None):
        """get the list of all your jobs

        Args:
            experiment_id (str): (optional) filter the job list by experiment, by default, will look in every experiment.
            workflow_id (str): (optional) filter the job list by workflow, by default, will look in every workflow.
        Returns:
            :py:class:`Job`
        """

        request = backend_pb2.ListJobsRequest(
            experiment_id=experiment_id,
            workflow_id=workflow_id,
        )
        try:
            response = self.job_stub.ListJobs(request)
            if response.status == backend_pb2.Status.Value("NOT_FOUND"):
                return JobList(ok=False, reason=response.reason)
            job_list = []
            for job_message in response.items:
                job_list.append(
                    {
                        "job_id": job_message.job_id,
                        "job_name": job_message.job_name,
                        "experiment_id": job_message.experiment_id,
                        "workflow_id": job_message.workflow_id,
                        "status": backend_pb2.Status.Name(job_message.status),
                    }
                )
            return JobList(items=job_list, ok=True)
        except grpc.RpcError as e:
            logger.error(e.details())
            return JobList(items=None, ok=False, reason=e.details())

    def run_job(self, name: str, workflow: str, input: dict = {}):
        """execute the selected experiment with the selected Job"""
        if not input:
            raise ValueError("No data loaded for this Job")

        request = backend_pb2.StartJobRequest(
            job_name=name,
            experiment_id=self.id,
            workflow_id=workflow,
            input=json.dumps(input),
        )
        response = self.job_stub.StartJob(request)
        if response.status == backend_pb2.Status.Value("ERROR"):
            logger.error(f"Could not start to process this Job. reason: {response.reason}")
            job = Job(
                job_stub=self.job_stub,
                id=response.job_id,
                workflow_id=workflow,
                experiment_id=self.id,
                name=name,
                status="ERROR",
                reason=response.reason,
                local_output_path=self.local_output_path,
            )
            return job
        elif response.status == backend_pb2.Status.Value("RUNNING"):
            job = Job(
                job_stub=self.job_stub,
                id=response.job_id,
                workflow_id=workflow,
                experiment_id=self.id,
                name=name,
                status="RUNNING",
                local_output_path=self.local_output_path,
            )
            logger.info(f"Experiment (id:{self.id}) Started for Job(id:{response.job_id})")
            return job

    @staticmethod
    def load_s1_ard_from_local(id: str, root_dir: str = "./generated"):
        """Load a previous S1 ARD computation result from local disk.

        Args:
            id (str): previously computed ARD id.
            root_dir(str): root directory where the ARD computation results are stored.

        Returns:
            :py:class:`Sentinel1Result`

        """

        items = []
        work_dir = os.path.join(root_dir, id)
        if not id:
            raise ValueError("id is required")
        if not os.path.isdir(work_dir):
            raise ValueError(f"Previous computation result with id {id} could not found ({work_dir})")
        for filename in os.listdir(work_dir):
            file_path = os.path.join(work_dir, filename)
            result = Sentinel1ResultItem(None, "success", file_path=file_path)
            items.append(result)
        return Sentinel1Result(items=items)

    @staticmethod
    def load_fusion(id: str, root_dir: str = "./generated"):
        """Load a previous fusion computation result from local disk.

        Args:
            id (str): previously computed fusion id.
            root_dir(str): root directory where the fusion computation results are stored.

        Returns:
            :py:class:`FuseResult`

        """
        work_dir = os.path.join(root_dir, id)
        if not id:
            raise ValueError("id is required")
        if not os.path.isdir(work_dir):
            raise ValueError(f"Previous computation result with id {id} could not found ({work_dir})")
        for filename in os.listdir(work_dir):
            file_path = os.path.join(work_dir, filename)
            result = FuseResult(client_id=id, base_dir=file_path, file_path=file_path)
        return result

    def weather_search(self, aoi, start_date, end_date, variables: List[str] = None) -> WeatherSearchResult:
        """
        Search for Weather data given area of interest. The data is computed from ERA5 reanalysis :
        `ERA5 Copernicus Climate Data Store <https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-single-levels?tab=overview>`_

        Parameters:
            aoi (geojson): A GeoJSON polygon
            start_date (str or datetime): Start date of the search
            end_date (str or datetime): End date of the search
            variables (list, optional): Weather variables desired

        :rtype: :py:class:`models.WeatherSearchResult`

        :return: :py:class:`models.WeatherSearchResult` object, continaing a pandas dataframe with the resulting weather data

        The following weather parameter are usable in the variables parameter:

            - "MAXTEMP": 2m_temperature maximum
            - "MINTEMP": 2m_temperature minimum
            - "AVGTEMP": 2m_temperature average
            - "PREC": total_precipitation
            - "VWIND": 10m_v_component_of_wind
            - "UWIND": 10m_u_component_of_wind
            - "LAILOW": leaf_area_index_low_vegetation
            - "LAIHIGH": leaf_area_index_high_vegetation
            - "DEWTEMP": 2m_dewpoint_temperature

        .. note:: weather_search by default returns average 2m temperature and total precipitation only.

        Example
        ----------
            >>> weather_variables = ["laihigh", "prec", "avgtemp", "dewtemp"]
            >>> weather_df = client.weather_search(aoi = aoi,
                                            start_date = start_date,
                                            end_date = end_date,
                                            variables = weather_variables)

        For more examples, please see the `Fusion with Weather <../notebooks/4_weather_insights.html>`_

        """
        aoi_param = Struct()
        aoi_param.update(aoi)

        if type(start_date) == str:
            start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()

        if type(start_date) != datetime.date:
            raise ValueError("Invalid start_date, should be a datetime.date object or a str in isoformat")

        if type(end_date) == str:
            end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()

        if type(end_date) != datetime.date:
            raise ValueError("Invalid end_date, should be a datetime.date object or a str in isoformat")

        if start_date == end_date:
            end_date = end_date + datetime.timedelta(days=1)
            logger.warning("start_date and end_date are the same, adding 1 day to end_date")

        variables_struct = Struct()
        if variables is not None:
            variables_struct.update({"variables": [v.lower() for v in variables]})
        else:
            variables_struct.update({"variables": ["mintemp", "maxtemp", "avgtemp", "prec"]})

        try:
            response = self.core_stub.GetWeatherSearch(
                backend_pb2.GetWeatherSearchRequest(
                    experiment_id=self.id,
                    aoi=aoi_param,
                    start_date=start_date.isoformat(),
                    end_date=end_date.isoformat(),
                    variables=variables_struct,
                )
            )
            weather_data = json_format.MessageToDict(response.data)

            return WeatherSearchResult(aoi, weather_data=weather_data)
        except grpc.RpcError as e:
            logger.error(e.details())
            return WeatherSearchResult(aoi, weather_data=None, ok=False, reason=e.details())


def _extract_scenes(scene_list_message: Struct) -> list:
    """
    Create a Sentinel1SceneList object from a protobuf message
    """
    return json_format.MessageToDict(scene_list_message).get("scenes")


def has_duplicates(list: list):
    """Check if given list contains any duplicates"""
    compare_set = set()
    for elem in list:
        if elem in compare_set:
            return elem
        else:
            compare_set.add(elem)
    return None


def has_empty_dataframe(list: list):
    """Check if given list contains empty dataset"""
    for elem in list:
        if elem.dataframe.empty:
            return elem
    return None
