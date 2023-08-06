import datetime
import json
from typing import Union

import pandas as pd
from satstac import Collection, ItemCollection


class Sentinel1SearchResult:
    """
    Create an instance of the Sentinel-1 Search Result class :py:class:`models.Sentinel1SearchResult`

    Attributes:
        aoi: A GeoJSON polygon passed from the :py:class:`client.Client.s1_search`
        data_coverage: 0 to 100 measure of the tile level data coverage for the result
        scenes: S1 scenes found matching the :py:class:`client.Client.s1_search`
        ok: Status output of the search, True indicates a valid return of the seach result
        reason: Description of the 'ok' status
        dataframe: The search result returned as a dataframe containing various properties (described below)
        output_bands: List of strings specifying the names of output bands from the following list of Sentinel-1 bands.

    By default, all bands are selected and fused. If overwriting the default bands, the fused result
    will keep the order specified in the "output_bands" parameter.\n
            - VV
            - VH
            - LIA
            - MASK


    To learn more about SAR polarization (VV and VH), LIA, and the processing steps we apply, please review our `SAR basics page <../geospatialfunds/sarbasics.html>`_.

    The following Sentinel-1 properties are available in the S1 search result, and are identical to those found from the `Copernicus Open Access Hub Search <https://scihub.copernicus.eu/userguide/FullTextSearch>`_:

    - title
    - date
    - relativeorbitnumber
    - lastrelativeorbitnumber
    - producttype
    - sensoroperationalmode
    - acquisitiontype
    - polarisationmode
    - beginposition
    - platformname
    - missiondatatakeid
    - orbitdirection
    - orbitnumber
    - instrumentname
    - lastorbitnumber
    - endposition
    - ingestiondate
    - slicenumber
    - platformidentifier
    """

    NAME = "s1"

    def __init__(self, aoi, data_coverage, scenes, ok: bool = True, reason: str = None):
        """
        Create an instance of the Sentinel-1 Search Result class :py:class:`models`
        """
        self.ok = ok
        self.reason = reason
        self.aoi = aoi
        self.data_coverage = data_coverage
        self.output_bands = ["VH", "VV", "DV", "LIA"]
        self._scenes = scenes
        if self._scenes:
            columns = [
                "title",
                "date",
                "swath_coverage_percentage",
                "relativeorbitnumber",
                "lastrelativeorbitnumber",
                "producttype",
                "sensoroperationalmode",
                "acquisitiontype",
                "polarisationmode",
                "beginposition",
                "platformname",
                "missiondatatakeid",
                "orbitdirection",
                "orbitnumber",
                "instrumentname",
                "lastorbitnumber",
                "endposition",
                "ingestiondate",
                "slicenumber",
                "platformidentifier",
            ]
            dataframe = pd.DataFrame(data=scenes, columns=columns)
            dataframe["date"] = pd.to_datetime(dataframe["date"])
            dataframe = dataframe.sort_values(["date"], ascending=True)
            self._dataframe = dataframe

    def has_results(self):
        return self.dataframe is not None and len(self.dataframe) > 0

    @property
    def output_bands(self):
        return self._output_bands

    @output_bands.setter
    def output_bands(self, bands: list):
        self._output_bands = [b.upper() for b in bands]

    @property
    def dataframe(self):
        if self.ok is False and self.reason:
            raise RuntimeError(f"S1 search result not ok: {self.reason}")
        else:
            return self._dataframe

    @dataframe.setter
    def dataframe(self, dataframe: pd.DataFrame):
        if type(dataframe) != pd.DataFrame:
            raise ValueError("dataframe should be a pandas.DataFrame")
        self._dataframe = dataframe
        self._scenes = [scene for scene in self._scenes if scene["title"] in self._dataframe["title"].values]

    @property
    def to_dict(self):
        dataframe = self.dataframe.copy()
        dataframe["date"] = dataframe["date"].dt.strftime("%Y-%m-%d")
        return dataframe.to_dict(orient="records")

    @staticmethod
    def concat(search_results):
        """
        Method to combine/concatenate multiple search results into a single :py:class:`models.Sentinel1SearchResult`.

        Example
        ----------
            >>> from spacesense import Client, Sentinel1SearchResult
            >>> client = Client()
            >>> res_S1_1 = client.s1_search(aoi, start_date, end_date)
            >>> res_S1_2 = client.s1_search(aoi, start_date_2, end_date_2)
            >>> res_S1 = Sentinel1SearchResult.concat([res_S1_1, res_S1_2])
        """
        if not search_results:
            raise ValueError("Nothing to concat")
        first_item = search_results[0]
        scenes = []
        for search_result in search_results:
            scenes.extend(search_result._scenes)
        return Sentinel1SearchResult(first_item.aoi, first_item.data_coverage, scenes)

    @property
    def grpc_message(self):
        result = {}
        result["bands"] = self.output_bands
        result["query_results"] = make_grpc_serializable(self.to_dict)
        return result

    def filter_duplicate_dates(self):
        """
        Finds any duplicate dates with the S1 search result and drops (filters) the duplicate item with the less covered orbit.
        If orbit coverage_percentage is the same in both results, the item that comes second in the dataframe index is dropped.
        """
        date_counts = self.dataframe.date.value_counts()
        for i in enumerate(date_counts):
            if i[1] > 1:
                dupe = self.dataframe[self.dataframe.date == date_counts.index[i[0]]]
                if dupe.swath_coverage_percentage.iloc[0] >= dupe.swath_coverage_percentage.iloc[1]:
                    self.dataframe = self.dataframe.drop(dupe.swath_coverage_percentage.index[1])
                else:
                    self.dataframe = self.dataframe.drop(dupe.swath_coverage_percentage.index[0])


class Sentinel2SearchResult:
    """
    Create an instance of the Sentinel-2 Search Result class :py:class:`models.Sentinel2SearchResult`.

    Attributes:
        aoi: A GeoJSON polygon passed from the :py:class:`client.Client.s2_search`
        item_collection: S2 scenes found matching the :py:class:`client.Client.s2_search`
        ok: Status output of the search, True indicates a valid return of the seach result
        reason: Description of the 'ok' status
        dataframe: The search result returned as a dataframe containing various properties (described below)
        output_bands: List of strings specifying the names of output bands from the following list of Sentinel-2 bands.


    By default, only B02, B03, B04, B08, and the SCL bands are selected and fused. If overwriting the default bands, the fused result
    will keep the order specified in the "output_bands" parameter.\n
            - B01
            - B02
            - B03
            - B04
            - B05
            - B06
            - B07
            - B08
            - B8A
            - B09
            - B11
            - B12
            - SCL

    B02, B03, B04 and B08 are also available with their color names:
            - BLUE
            - GREEN
            - RED
            - NIR

    Please note, Band 10 is not available for level 2A Sentinel-2 data, as this band is used for atmospheric corrections only.

    We also provide several pre-computed vegetation indices (VIs) from Sentinel-2 data. For details about these VIs, please see `this page <../geospatialfunds/vegetationindex.html>`_.
    The following VIs can be selected and fused along with the previously enumerated bands: \n
            - NDVI
            - LAI
            - NDRE
            - CHI
            - NDWI
            - EVI

    The Sentinel-2 data retrieved is L2A, meaning it represents the bottom of the atmosphere (BOA) reflectance values.
    `This link <https://www.esa.int/Applications/Observing_the_Earth/Copernicus/Sentinel-2/Data_products>`_ describes Sentinel-2 data levels and products.

    To learn about the Sentinel-2 data levels, bands, and scene classifications, to help you select the right data for your use case, please visit our `Optial Basics page <../geospatialfunds/opticalbasics.html>`_

    The following Sentinel-2 properties are available in the S2 search result:

    - id
    - date
    - tile
    - valid_pixel_percentage
    - platform
    - relative_orbit_number
    - product_id
    - datetime
    - swath_coverage_percentage
    - no_data*
    - cloud_shadows*
    - vegetation*
    - not_vegetated*
    - water*
    - cloud_medium_probability*
    - cloud_high_probability*
    - thin_cirrus*
    - snow*

    **swath_coverage_percentage** is simply the percentage of data covered by the Sentinel-2 swath at the AOI level.

    **valid_pixel_percentage** is defined as a percentage of the combination of pixels, at the AOI level, NOT classified as no_data,
    cloud_shadows, cloud_medium_probability, cloud_high_probability, and snow.
    This is a very useful property to use when determining if a Sentinel-2 scene clear of clouds and snow for vegetation and infrastructure monitoring.

    **"*"** denotes that the property is a direct calculation of the percent coverage of the associated SCL bands over the AOI.

    """

    NAME = "s2"

    def __init__(self, aoi, item_collection: ItemCollection, ok: bool = True, reason: str = None):
        """
        Create an instance of the Sentinel-2 Search Result class :py:class:`models`.
        """

        self.ok = ok
        self.reason = reason
        self.aoi = aoi
        self._item_collection = item_collection
        if item_collection:
            self._dataframe = self.metadata_dataframe_from_item_collection(item_collection)
        self.output_bands = ["B02", "B03", "B04", "B08", "SCL"]

    def has_results(self):
        return self.dataframe is not None and len(self.dataframe) > 0

    @property
    def output_bands(self):
        return self._output_bands

    @property
    def count(self):
        return len(self._item_collection._items)

    @output_bands.setter
    def output_bands(self, bands: list):
        self._output_bands = [b.upper() for b in bands]

    @property
    def dataframe(self):
        if self.ok is False and self.reason:
            raise RuntimeError(f"S2 search result not ok: {self.reason}")
        else:
            return self._dataframe

    @dataframe.setter
    def dataframe(self, dataframe: pd.DataFrame):
        if type(dataframe) != pd.DataFrame:
            raise ValueError("dataframe should be a pandas.DataFrame")
        self._dataframe = dataframe
        self._item_collection = self.item_collection_from_metadata_dataframe()

    @property
    def item_collection(self):
        return self._item_collection

    @item_collection.setter
    def item_collection(self, item_collection: ItemCollection):
        if type(item_collection) != ItemCollection:
            raise ValueError("item_collection should be an ItemCollection")
        self._item_collection = item_collection
        self._dataframe = self.metadata_dataframe_from_item_collection()

    @property
    def to_dict(self):
        return self._item_collection.geojson()

    @property
    def grpc_message(self):
        result = {}
        result["bands"] = self.output_bands
        result["query_results"] = make_grpc_serializable(self.to_dict)
        return result

    def metadata_dataframe_from_item_collection(self, item_collection: ItemCollection = None) -> pd.DataFrame:
        item_collection = item_collection or self._item_collection
        meta = [item.properties["spacesense"] for item in item_collection]
        columns = [
            "id",
            "date",
            "tile",
            "valid_pixel_percentage",
            "platform",
            "relative_orbit_number",
            "product_id",
            "datetime",
            "swath_coverage_percentage",
            "no_data",
            "cloud_shadows",
            "vegetation",
            "not_vegetated",
            "water",
            "cloud_medium_probability",
            "cloud_high_probability",
            "thin_cirrus",
            "snow",
        ]
        df = pd.DataFrame(data=meta, columns=columns)
        df = df.sort_values(["date"], ascending=True)
        df["date"] = pd.to_datetime(df["date"])
        return df

    def item_collection_from_metadata_dataframe(self):
        ids = list(self._dataframe.id)
        self._item_collection._items = [item for item in self._item_collection._items if item.id in ids]
        return self._item_collection

    @staticmethod
    def concat(search_results):
        """
        Method to combine/concatenate multiple search results into a single :py:class:`models.Sentinel2SearchResult`.

        Example
        ----------
            >>> from spacesense import Client, Sentinel2SearchResult
            >>> client = Client()
            >>> res_S2_1 = client.s1_search(aoi, start_date, end_date)
            >>> res_S2_2 = client.s1_search(aoi, start_date_2, end_date_2)
            >>> res_S2 = Sentinel2SearchResult.concat([res_S2_1, res_S2_2])
        """

        if not search_results:
            raise ValueError("Nothing to concat")
        first_item = search_results[0]
        items = []
        collections = []
        for search_result in search_results:
            items.extend(search_result.item_collection._items)
            collections.extend(
                [Collection(collection) for collection in search_result.item_collection.geojson()["collections"]]
            )

        result = Sentinel2SearchResult(first_item.aoi, ItemCollection(items, collections))
        return result

    def filter_duplicate_dates(self):
        """
        Finds any duplicate dates with the S2 search result and drops (filters) the duplicate item with the lowest valid_pixel_percentage (if different).
        If valid_pixel_percentage is the same in both results, the item that comes second in the dataframe index is dropped.
        """
        self.dataframe = self.dataframe.groupby("date", group_keys=False).apply(
            lambda x: x.loc[x.valid_pixel_percentage.idxmax()]
        )


class WeatherSearchResult:
    """
    Create an instance of the Weather Search Result class :py:class:`models.WeatherSearchResult`

    Attributes:
        aoi: A GeoJSON polygon passed from the :py:class:`client.Client.weather_search`
        ok: Status output of the search, True indicates a valid return of the seach result
        reason: Description of the 'ok' status
        dataframe: The search result returned as a dataframe containing various properties (described below)

    By default, all bands are selected and fused. If overwriting the default bands, the fused result
    will keep the order specified in the "variables" parameter.\n
            - MAXTEMP
            - MINTEMP
            - AVGTEMP
            - PREC
            - VWIND
            - UWIND
            - LAILOW
            - LAIHIGH
            - DEWTEMP


    To learn more the weather variables please visit `ERA5 Copernicus Climate Data Store <https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-single-levels?tab=overview>`_.
    """

    NAME = "weather"

    def __init__(self, aoi, weather_data, ok: bool = True, reason: str = None):
        self.ok = ok
        self.reason = reason
        self.aoi = aoi
        if weather_data:
            self._info = weather_data["info"]
            self._data = json.loads(weather_data["data"])
            dataframe = pd.DataFrame(data=self._data)
            dataframe["date"] = pd.to_datetime(dataframe["date"])
            dataframe = dataframe.sort_values(["date"], ascending=True)
            self._dataframe = dataframe

    @property
    def dataframe(self):
        if self.ok is False and self.reason:
            raise RuntimeError(f"Weather search result not ok: {self.reason}")
        else:
            return self._dataframe

    @dataframe.setter
    def dataframe(self, dataframe: pd.DataFrame):
        if type(dataframe) != pd.DataFrame:
            raise ValueError("dataframe should be a pandas.DataFrame")
        self._dataframe = dataframe

    @property
    def to_dict(self):
        dataframe = self.dataframe.copy()
        dataframe["date"] = dataframe["date"].dt.strftime("%Y-%m-%d")
        return dataframe.to_dict(orient="records")

    @property
    def additional_info(self):
        return self._additional_info

    @property
    def grpc_message(self):
        result = {}
        result["data"] = make_grpc_serializable(json.dumps(self.to_dict))
        result["info"] = make_grpc_serializable(self._info)
        return result


def make_grpc_serializable(d: Union[dict, list]) -> Union[dict, list]:
    """
    Make a dictionary serializable for gRPC
    """
    if type(d) is dict:
        iterator_with_key = d.items()
    elif type(d) is list:
        iterator_with_key = enumerate(d)
    else:
        return d

    for key, value in iterator_with_key:
        if isinstance(value, datetime.datetime) or isinstance(value, datetime.date):
            d[key] = value.isoformat()
        elif type(value) is dict or type(value) is list:
            d[key] = make_grpc_serializable(value)
        else:
            continue
    return d
