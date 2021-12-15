# -*- coding: utf-8 -*-
import json
import logging
from enum import Enum
from typing import cast
from typing import Dict
from typing import List
from typing import Union

import geopandas as gpd
import pandas as pd

from ..dal import Stac
from ..dal import StacEnum
from ..iwidget import GeoJSONLayer
from ..iwidget import PluginVisu
from ..iwidget import Surface
from ..iwidget import WMSLayer
from ..iwidget.mizar import Mizar

JSON = Union[None, bool, str, float, int, List["JSON"], Dict[str, "JSON"]]

logger = logging.getLogger(__name__)


class IPlanet:
    pass
    # Create interface


class PlanetEnum(Enum):

    MARS = "MARS"
    EARTH = "EARTH"


class PlanetFactory:
    @staticmethod
    def load(url: str, max_records: int = None) -> IPlanet:
        gdf: gpd.GeoDataFrame = Stac.load(StacEnum.ITEM, url, max_records)
        planet_name: str
        if "ssys:targets" in gdf.columns:
            planet_name = (gdf["ssys:targets"].iloc[0])[0]
        else:
            planet_name = "Mars"

        planet: IPlanet
        if planet_name.upper() == PlanetEnum.MARS.value:
            planet = Mars(gdf)
        elif planet_name.upper() == PlanetEnum.EARTH.value:
            planet = Earth(gdf)
        else:
            raise NotImplementedError("Only Mars is implemented as planet")

        return planet


class MarsVisu(Mizar):
    def __init__(self):
        super().__init__()
        wms = WMSLayer(
            name="wms_mars",
            format="png",
            url="https://idoc-wmsmars.ias.u-psud.fr/cgi-bin/mapserv?map=/home/cnes/mars/mars.map",
            layers="viking",
            background=True,
        )
        self.add_layer(wms)

    def add_layer_wms(self, base_url, layer_name):
        wms = WMSLayer(
            name=layer_name,
            format="png",
            url=base_url,
            layers=layer_name,
            background=False,
            transparent=True,
        )
        self.add_layer(wms)


class EarthVisu(Mizar):
    def __init__(self):
        super().__init__()
        wms = WMSLayer(
            name="wms_mars",
            format="png",
            url="https://regards-pp.cnes.fr/api/v1/hysope/?map=/etc/mapserver/bluemarble.map",
            layers="BlueMarble",
            background=True,
        )
        self.add_layer(wms)

    def add_layer_wms(self, base_url, layer_name):
        wms = WMSLayer(
            name=layer_name,
            format="png",
            url=base_url,
            layers=layer_name,
            background=False,
            transparent=True,
        )
        self.add_layer(wms)


class Mars(IPlanet):

    NAME = PlanetEnum.MARS.value

    def __init__(self, data: gpd.GeoDataFrame):
        self.__data: gpd.GeoDataFrame = data

    def _add_geojson(
        self,
        mars_visu: MarsVisu,
        data: gpd.GeoDataFrame,
        color: List[float] = [0, 190, 100, 1],
    ) -> None:
        observations = GeoJSONLayer(
            name="data",
            data=json.loads(data.to_json()),
            style={"strokeColor": color, "opacity": 1},
        )
        mars_visu.add_layer(observations, center=True)

    def describe(self) -> str:
        return self.data.describe(include="all")

    def query(
        self,
        query: str,
        mars_visu: MarsVisu = None,
        color: List[float] = [0, 190, 100, 1],
    ) -> gpd.GeoDataFrame:
        result: gpd.GeoDataFrame = self.data.query(query)
        if mars_visu is not None:
            self._add_geojson(mars_visu, result, color)
        return result

    def histogram(
        self, color="k", alpha=0.5, bins=50, figsize=(10, 10)
    ) -> None:
        numerics = ["int16", "int32", "int64", "float16", "float32", "float64"]
        newdf = self.data.select_dtypes(include=numerics)
        newdf.hist(color, alpha, bins, figsize)

    def visu3D(self) -> MarsVisu:
        mars: MarsVisu = MarsVisu()
        heatmap_url: Union[None, str] = self.data["heatmap"].iloc[0]
        if heatmap_url is not None:
            from urllib.parse import urlparse, parse_qs

            url_parse = urlparse(heatmap_url)
            base_url = (
                f"{url_parse.scheme}://{url_parse.netloc}/{url_parse.path}"
            )
            layer_name = parse_qs(url_parse.query)["layers"][0]
            mars.add_layer_wms(base_url, layer_name)
        return mars

    def has_preview(self):
        pass

    def show_image(self):
        pass

    def show_dataset_visu3D(
        self, mars_visu: MarsVisu, color: List[float] = [0, 190, 100, 1]
    ) -> None:
        self._add_geojson(mars_visu, self.data, color)

    def remove_dataset_visu3D(self, mars_visu: MarsVisu) -> None:
        mars_visu.remove_layer("data")

    def columns(self) -> List[str]:
        return list(self.data.columns)

    def highlight(
        self, mars_visu: MarsVisu, index: Union[List, int], color=[1, 0, 0, 1]
    ):
        selection: gpd.GeoDataFrame
        if isinstance(index, int):
            selection = self.data.iloc[index : index + 1]
        else:
            selection = self.data.iloc[index]
        mars_visu.highlight(json.loads(selection.to_json()), color)

    def highlight_by_index(
        self, mars_visu: MarsVisu, index: pd.Index, color=[1, 0, 0, 1]
    ):
        selection: gpd.GeoDataFrame = self.data.loc[index]
        mars_visu.highlight(json.loads(selection.to_json()), color)

    def remove_highlight(self, mars_visu: MarsVisu):
        mars_visu.highlight(None)

    @property
    def data(self) -> gpd.GeoDataFrame:
        return self.__data


class Earth(IPlanet):

    NAME = PlanetEnum.EARTH.value

    def __init__(self, data: gpd.GeoDataFrame):
        self.__data: gpd.GeoDataFrame = data

    def _add_geojson(
        self,
        earth_visu: EarthVisu,
        data: gpd.GeoDataFrame,
        color: List[float] = [0, 190, 100, 1],
    ) -> None:
        observations = GeoJSONLayer(
            name="data",
            data=json.loads(data.to_json()),
            style={"strokeColor": color, "opacity": 1},
        )
        earth_visu.add_layer(observations, center=True)

    def describe(self) -> str:
        return self.data.describe(include="all")

    def query(
        self,
        query: str,
        earth_visu: EarthVisu = None,
        color: List[float] = [0, 190, 100, 1],
    ) -> gpd.GeoDataFrame:
        result: gpd.GeoDataFrame = self.data.query(query)
        if earth_visu is not None:
            self._add_geojson(earth_visu, result, color)
        return result

    def histogram(
        self, color="k", alpha=0.5, bins=50, figsize=(10, 10)
    ) -> None:
        numerics = ["int16", "int32", "int64", "float16", "float32", "float64"]
        newdf = self.data.select_dtypes(include=numerics)
        newdf.hist(color, alpha, bins, figsize)

    def visu3D(self) -> EarthVisu:
        earth: EarthVisu = EarthVisu()
        heatmap_url: Union[None, str] = self.data["heatmap"].iloc[0]
        if heatmap_url is not None:
            from urllib.parse import urlparse, parse_qs

            url_parse = urlparse(heatmap_url)
            base_url = (
                f"{url_parse.scheme}://{url_parse.netloc}/{url_parse.path}"
            )
            layer_name = parse_qs(url_parse.query)["layers"][0]
            earth.add_layer_wms(base_url, layer_name)
        return earth

    def has_preview(self):
        pass

    def show_image(self):
        pass

    def show_dataset_visu3D(
        self, earth_visu: EarthVisu, color: List[float] = [0, 190, 100, 1]
    ) -> None:
        self._add_geojson(earth_visu, self.data, color)

    def remove_dataset_visu3D(self, earth_visu: EarthVisu) -> None:
        earth_visu.remove_layer("data")

    def columns(self) -> List[str]:
        return list(self.data.columns)

    def highlight(
        self,
        earth_visu: EarthVisu,
        index: Union[List, int],
        color=[1, 0, 0, 1],
    ):
        selection: gpd.GeoDataFrame
        if isinstance(index, int):
            selection = self.data.iloc[index : index + 1]
        else:
            selection = self.data.iloc[index]
        earth_visu.highlight(json.loads(selection.to_json()), color)

    def highlight_by_index(
        self, earth_visu: EarthVisu, index: pd.Index, color=[1, 0, 0, 1]
    ):
        selection: gpd.GeoDataFrame = self.data.loc[index]
        earth_visu.highlight(json.loads(selection.to_json()), color)

    def remove_highlight(self, earth_visu: EarthVisu):
        earth_visu.highlight(None)

    @property
    def data(self) -> gpd.GeoDataFrame:
        return self.__data
