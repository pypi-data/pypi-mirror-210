import logging
import os

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
from shapely.geometry import Point
from sklearn.cluster import KMeans

logger = logging.getLogger(__name__)


def measure_distance(ds: xr.Dataset, SCL_val: int, lon: float, lat: float, plot: bool = True) -> float:
    """
    Function to calculate the distance from a specified longitude and latitude to the scene classification specified. The scene classification is taken from the first index on the Sentinel-2 SCL
    band in the fused result. The function returns the distance in meters, and plots the distance in a circle around the specified location.

    To use this function, you must pass a Sentinel-2 dataset with the SCL band already fused. Please ensure that clouds are minimal or nonexistant,
    as that can impact the location of the scene classificaitons in the SCL band.

    Args:
        ds (xr.Dataset): Dataset to measure
        SCL_val (int): Sentinel SCL band number representing classification to measure distance to
        lon (float): Longitude of point of interest to measure from
        lat (float): Latitude of point of interest to measure from
        plot (bool): Plot figure of distance measure

    :rtype: float

    Returns:
        Minimum distance from point of interest to the specified classification
    """
    if "spatial_ref" in ds.coords:
        ds = ds.drop(["spatial_ref"])
    if "time" in ds.coords:
        ds = ds.drop(["time"])
    ds["mask_val"] = (ds["S2_SCL"][0] == SCL_val) * 1

    # Polygonize
    x, y, mask_val = ds.x.values, ds.y.values, ds["mask_val"].values
    x, y = np.meshgrid(x, y)
    x, y, mask_val = x.flatten(), y.flatten(), mask_val.flatten()

    df = pd.DataFrame.from_dict({"mask_val": mask_val, "x": x, "y": y})
    threshold = 0.5
    df = df[df["mask_val"] > threshold]
    vector = gpd.GeoDataFrame(geometry=gpd.GeoSeries.from_xy(df["x"], df["y"]), crs="EPSG:4326")
    vector = vector.to_crs("EPSG:3857")
    vector = vector.buffer(5, cap_style=3)
    loc = Point(lon, lat)
    gdf = gpd.GeoDataFrame({"location": [1], "geometry": [loc]}, crs="EPSG:4326")
    gdf = gdf.to_crs(3857)
    vector = vector.to_crs(3857)
    wat_dist = vector.distance(gdf["geometry"][0])
    min_dist = round(min(wat_dist), 2)
    logger.info(f"Minimal distance to nearest specified classification: {min_dist} [m]")

    # Plot
    if plot is True:
        fig, ax = plt.subplots(1, 1)
        circle1 = plt.Circle((gdf["geometry"].x, gdf["geometry"].y), min_dist, fill=False)
        ax.add_patch(circle1)
        vector.plot(ax=ax)
        gdf.plot(color="None", edgecolor="red", linewidth=2, zorder=1, ax=ax)
        plt.show()

    return min_dist


def cluster(dataset, n_clusters=5, variable_prefixes=None, save=False, save_path=None):
    """
    Function to perform K-means clustering on an area of interest (AOI) dataset. This function takes an input dataset and performs K-means clustering on it, returning a clustered dataset. Optionally, you can save the clustered image to a specified directory.

    Args:
        dataset (xarray.Dataset) : The input dataset containing data to be clustered.
        n_clusters (int, optional) : The number of clusters to create, default is 5.
        variable_prefixes (list, optional) : A list of variable prefixes to use for clustering. If not specified, all variables in the dataset will be used.
        save (bool, optional) : Whether to save the clustered image, default is False.
        save_path (str, optional) : The directory path to save the clustered image to. Required if save is set to True.

    :rtype: xarray.Dataset

    Returns:
        The clustered dataset with an additional 'cluster' DataArray representing the cluster labels.

    """
    filtered_dataset = None
    if variable_prefixes is not None:
        variables = [var for layer in variable_prefixes for var in dataset.data_vars if var.startswith(layer)]
        filtered_dataset = dataset[variables]

    if "time" in dataset.dims:
        flattened_dataset = flatten_time_variables(filtered_dataset or dataset)
    else:
        flattened_dataset = filtered_dataset or dataset

    # Stack x, y dimensions into a single 'pixel' dimension
    stacked_data = flattened_dataset.stack(pixel=["x", "y"])

    # Drop NaN values
    stacked_data = stacked_data.dropna(dim="pixel", how="any")

    # Convert the data to a 2D numpy array
    data_array = stacked_data.to_array().values

    # Transpose the array to have pixels as rows and bands as columns
    data_array_T = np.reshape(data_array, (data_array.shape[0], -1)).T

    # Perform K-means clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(data_array_T)
    cluster_labels = kmeans.labels_

    # Create a new DataArray with the same dimensions as the input dataset
    new_data_array = xr.DataArray(
        data=cluster_labels, coords={"pixel": stacked_data.pixel}, dims=["pixel"], name="cluster"
    )

    # Unstack the 'pixel' dimension back to the original 'x', 'y' dimensions
    new_data_array = new_data_array.unstack("pixel")

    # Assign the new cluster DataArray to the original dataset
    clustered_dataset = dataset.assign(cluster=new_data_array)

    # Add the cluster centers values to the dataset attributes
    cluster_centers = kmeans.cluster_centers_
    wrapper_dict = {"cluster_centers": {}}
    for i in range(n_clusters):
        cluster_centers_dict = {
            f"cluster_{i}_{var}": cluster_centers[i, j] for j, var in enumerate(stacked_data.data_vars)
        }
        wrapper_dict["cluster_centers"].update(cluster_centers_dict)
    clustered_dataset.attrs.update(wrapper_dict)

    # Save the clustered image if requested
    if save:
        if not (save_path and os.path.isdir(os.path.dirname(save_path))):
            raise ValueError("save_path must be specified if save is True")
        clustered_dataset.to_netcdf(save_path, mode="w", format="NETCDF4")

    return clustered_dataset


def flatten_time_variables(dataset):
    """
    Flatten the time variables in a dataset by creating new variables for each band and date combination. Removes the time dimension.

    Args:
    dataset (xarray.Dataset): The input dataset with time variables.

    Returns:
    xarray.Dataset: A new dataset with flattened time variables.
    """

    flattened_dataset = xr.Dataset()
    for var in dataset.data_vars:
        for t in range(len(dataset.time)):
            time_str = dataset.time[t].dt.strftime("%Y-%m-%d").item()
            new_var_name = f"{var}_{time_str}"
            flattened_dataset[new_var_name] = dataset[var].isel(time=t)
        # Preserve the attributes of the original variable
        flattened_dataset[new_var_name].attrs = dataset[var].attrs
    # Preserve the attributes of the original dataset
    flattened_dataset.attrs = dataset.attrs
    return flattened_dataset


def plot_clustered_dataset(clustered_dataset, n_clusters):
    """
    Plot a clustered dataset using the viridis colormap.

    Args:
        clustered_dataset (xarray.Dataset): The clustered dataset to plot.

    """

    # Use the viridis colormap and truncate it to the number of clusters
    cmap = plt.cm.get_cmap("viridis", n_clusters)
    custom_cmap = ListedColormap(cmap.colors)

    # Assuming 'clustered_dataset' is the result of the 'cluster_aoi' function
    cluster_data = clustered_dataset["cluster"]
    cluster_data = cluster_data.transpose("y", "x")

    # Create a plot with the custom color map
    fig, ax = plt.subplots()
    im = ax.imshow(cluster_data, cmap=custom_cmap, aspect="equal")
    ax.set_title("Cluster Map")

    # Create legend elements
    legend_elements = [
        Patch(facecolor=im.cmap(im.norm(c)), edgecolor="k", label=f"Cluster {c}") for c in range(n_clusters)
    ]

    # Add the legend to the plot
    plt.legend(handles=legend_elements, bbox_to_anchor=(1.05, 1), loc="upper left", title="Clusters")
    plt.tight_layout()
    plt.show()
