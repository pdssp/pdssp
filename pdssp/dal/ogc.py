# -*- coding: utf-8 -*-
import json
import logging
import re
import time
from typing import List

import geopandas as gpd
import pandas as pd
import requests
from owslib.feature.wfs110 import ContentMetadata as WfsContentMetadata
from owslib.map.wms111 import ContentMetadata as WmsContentMetadata
from owslib.wfs import WebFeatureService
from owslib.wms import WebMapService
from pyproj.crs.crs import CRS
from shapely.geometry import box

logger = logging.getLogger(__name__)


class Wfs:

    CRS_WKT = CRS.from_wkt(
        'GEOGCS["Mars 2000",DATUM["D_Mars_2000",SPHEROID["Mars_2000_IAU_IAG",3396190.0,169.89444722361179]],PRIMEM["Greenwich",0],UNIT["Decimal_Degree",0.0174532925199433]]'
    )
    MAX_REQUESTS = 10000

    def __init__(self, url: str, version: str = "2.0.0", **kwargs):
        self.__url: str = url
        self.__version: str = version
        self.__wfs: WebFeatureService = WebFeatureService(
            url=url, version=version
        )
        self.__ignore_layers: List[str] = (
            kwargs["ignore_layers"] if "ignore_layers" in kwargs else list()
        )

    @property
    def url(self):
        return self.__url

    @property
    def version(self):
        return self.__version

    @property
    def wfs(self):
        return self.__wfs

    @property
    def service_type(self):
        return self.wfs.identification.type

    @property
    def service_version(self):
        return self.wfs.identification.version

    @property
    def title(self):
        return self.wfs.identification.title

    @property
    def abstract(self):
        return self.wfs.identification.abstract

    @property
    def accessconstraints(self):
        return self.wfs.identification.accessconstraints

    @property
    def fees(self):
        return self.wfs.identification.fees

    @property
    def versions(self):
        return self.wfs.identification.versions

    @property
    def provider_name(self) -> str:
        return self.wfs.provider.name

    @property
    def layers(self) -> List[str]:
        return [
            layer
            for layer in self.wfs.contents
            if layer not in self.ignore_layers
        ]

    @property
    def ignore_layers(self) -> List[str]:
        return self.__ignore_layers

    def _retrieve_all_features(
        self, layer_name: str, start_index: int, max_features: int, count: int
    ) -> gpd.GeoDataFrame:
        logger.info(
            f"\tRetrieving from {start_index} to {start_index+max_features} on {count}"
        )
        try:
            features = self.wfs.getfeature(
                typename=layer_name,
                outputFormat="application/json",
                startindex=start_index,
                maxfeatures=max_features,
            )
            data_utf8 = features.read().decode("UTF-8")
            gdf = gpd.read_file(data_utf8)
            return gdf
        except requests.exceptions.ReadTimeout:
            time.sleep(10)
            self._retrieve_all_features(
                layer_name, start_index, max_features, count
            )
        except requests.exceptions.ConnectionError:
            time.sleep(10)
            self._retrieve_all_features(
                layer_name, start_index, max_features, count
            )

    def has_layer(self) -> bool:
        return len(self.layers) > 0

    def get_data(self, layer_name: str) -> gpd.GeoDataFrame:
        if layer_name not in self.layers:
            raise RuntimeError(f"Layer {layer_name} does not exist")

        count: int = self.get_count(layer_name)
        list_gdf: List[gpd.GeoDataFrame] = [
            self._retrieve_all_features(
                layer_name, start_index, Wfs.MAX_REQUESTS, count
            )
            for start_index in range(0, count - 1, Wfs.MAX_REQUESTS)
        ]
        if len(list_gdf) == 0:
            logger.warning(f"WARNING: Cannot retrieve data from {layer_name}")
            # TODO : faire quelque chose pour skipper
        gdf: gpd.GeoDataFrame = pd.concat(list_gdf, ignore_index=True)
        gdf.set_crs(Wfs.CRS_WKT, allow_override=True)
        logger.debug(
            f"{gdf.shape[0]} records have been retrieved in {layer_name}"
        )
        return gdf

    def get_schema(self, layer_name: str) -> json:
        if layer_name not in self.layers:
            raise RuntimeError(f"Layer {layer_name} does not exist")

        return self.wfs.get_schema(typename=layer_name)

    def get_layer(self, layer_name: str) -> WfsContentMetadata:
        if layer_name not in self.layers:
            raise RuntimeError(f"Layer {layer_name} does not exist")

        return self.wfs.contents[layer_name]

    def get_crs(self, layer_name: str) -> List:
        if layer_name not in self.layers:
            raise RuntimeError(f"Layer {layer_name} does not exist")

        return self.wfs.contents[layer_name].crsOptions

    def get_count(self, layer_name: str) -> int:
        params = {
            "service": "wfs",
            "version": self.version,
            "request": "GetFeature",
            "typeNames": layer_name,
            "resultType": "hits",
        }
        r = requests.get(url=self.url, params=params)
        txt = r.text
        m = re.search('numberMatched="([0-9]+)"', txt)
        nb = 0
        if m:
            nb = int(m.group(1))
        return nb


class Wms:
    def __init__(self, url: str, version: str = "1.1.1", **kwargs):
        self.__url = url
        self.__version = version
        self.__wms = WebMapService(url=url, version=version)
        self.__ignore_layers = (
            kwargs["ignore_layers"] if "ignore_layers" in kwargs else list()
        )

    @property
    def url(self):
        return self.__url

    @property
    def version(self):
        return self.__version

    @property
    def wms(self):
        return self.__wms

    @property
    def service_type(self):
        return self.wms.identification.type

    @property
    def service_version(self):
        return self.wms.identification.version

    @property
    def title(self):
        return self.wms.identification.title

    @property
    def abstract(self):
        return self.wms.identification.abstract

    @property
    def accessconstraints(self):
        return self.wms.identification.accessconstraints

    @property
    def fees(self):
        return self.wms.identification.fees

    @property
    def provider_name(self) -> str:
        return self.wms.provider.name

    @property
    def layers(self) -> List[str]:
        return [
            layer
            for layer in self.wms.contents
            if layer not in self.ignore_layers
        ]

    @property
    def ignore_layers(self) -> List[str]:
        return self.__ignore_layers

    def has_layer(self) -> bool:
        return len(self.layers) > 0

    def get_layer(self, layer_name: str) -> WmsContentMetadata:
        if layer_name not in self.layers:
            raise RuntimeError(f"Layer {layer_name} does not exist")

        return self.wms.contents[layer_name]

    def get_crs(self, layer_name: str) -> List:
        if layer_name not in self.layers:
            raise RuntimeError(f"Layer {layer_name} does not exist")

        return self.wms.contents[layer_name].crsOptions

    def get_data(self, layer_name: str) -> gpd.GeoDataFrame:
        if layer_name not in self.layers:
            raise RuntimeError(f"Layer {layer_name} does not exist")
        layer = self.get_layer(layer_name)
        metadata = layer.__dict__
        data = list()
        for key in metadata.keys():
            data.append(metadata[key])

        df = pd.DataFrame([data], columns=list(metadata.keys()))
        geometry = [
            box(poly[0], poly[1], poly[2], poly[3])
            for poly in df["boundingBox"]
        ]
        gdf = gpd.GeoDataFrame(df, geometry=geometry)
        gdf.set_crs(Wfs.CRS_WKT, allow_override=True)
        return gdf
