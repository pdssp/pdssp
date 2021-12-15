# -*- coding: utf-8 -*-
import logging
import ssl
from enum import Enum
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import geopandas as gpd
import pandas as pd
import requests
import swifter

JSON = Union[None, bool, str, float, int, List["JSON"], Dict[str, "JSON"]]

logger = logging.getLogger(__name__)


ssl._create_default_https_context = ssl._create_unverified_context


class StacEnum(Enum):
    ITEM = "item"


class StacItem:
    def __init__(self, url: str, max_records: int = None):
        self.__url: str = url
        self.__data: gpd.GeoDataFrame
        self.__max_records: Optional[int] = max_records
        self._load()

    def _load(self) -> None:
        pages: List[gpd.GeoDataFrame] = list()
        current_nb_records: int = 0
        self._get_next_page(self.url, pages, current_nb_records)
        self.__data = pd.concat(pages, ignore_index=True)
        self.__data = self.__data.iloc[0 : self.max_records]
        self.__data = self.__data.swifter.apply(self._create_columns, axis=1)
        self.__data.set_index("datetime", inplace=True)
        self.__data.sort_index(inplace=True)

    def _parse_hastags(self, row) -> None:
        if "hashtags" not in row:
            return
        tags = row["hashtags"]
        for tag in tags:
            (key, value) = tag.split(":", maxsplit=1)
            row[key] = value if key not in row else row[key] + "," + value

    def _parse_assets(self, row: gpd.GeoSeries) -> None:
        if "assets" not in row:
            return
        assets = row["assets"]
        for key in assets.keys():
            row[key] = assets[key]["href"]

    def _create_columns(self, row: gpd.GeoSeries) -> gpd.GeoSeries:
        self._parse_hastags(row)
        self._parse_assets(row)
        return row

    def _has_reach_max_records(self, current_nb_records: int) -> bool:
        if self.max_records is None:
            return False
        return current_nb_records >= self.max_records

    def _get_next_url(self, data_json) -> Union[None, str]:
        next_url = None
        links = data_json["links"]
        for link in links:
            if link["rel"] == "next":
                next_url = link["href"]
                break
        return next_url

    def _get_heatmap_url(self, data_json) -> Union[None, str]:
        heatmap_url = None
        links = data_json["links"]
        for link in links:
            if link["rel"] == "heatmap":
                heatmap_url = link["href"]
        return heatmap_url

    def _go_to_next_page(
        self,
        data_json: JSON,
        pages: List[gpd.GeoDataFrame],
        new_nb_records: int,
    ) -> None:
        next_url: Union[None, str] = self._get_next_url(data_json)
        if next_url is not None and not self._has_reach_max_records(
            new_nb_records
        ):
            logger.debug(next_url)
            self._get_next_page(next_url, pages, new_nb_records)

    def _get_next_page(
        self, url: str, pages: List[gpd.GeoDataFrame], current_nb_records: int
    ) -> None:
        data = requests.get(url)
        data_json = data.json()
        gdf: gpd.GeoDataFrame = gpd.GeoDataFrame.from_features(
            data_json["features"]
        )
        gdf_tmp: gpd.GeoDataFrame = gpd.GeoDataFrame(data_json["features"])
        if "assets" in gdf_tmp.columns:
            gdf["assets"] = gdf_tmp["assets"]
        gdf["heatmap"] = self._get_heatmap_url(data_json)
        nb_records: int = gdf.shape[0]
        new_nb_records: int = current_nb_records + nb_records
        pages.append(gdf)
        self._go_to_next_page(data_json, pages, new_nb_records)

    @property
    def url(self) -> str:
        return self.__url

    @property
    def data(self) -> gpd.GeoDataFrame:
        return self.__data

    @property
    def max_records(self) -> Union[None, int]:
        return self.__max_records

    def number_records(self) -> int:
        return self.data.size[0]


class Stac:
    @staticmethod
    def load(
        type: StacEnum, url: str, max_records: int = None
    ) -> gpd.GeoDataFrame:
        data: gpd.GeoDataFrame
        if type == StacEnum.ITEM:
            data = StacItem(url, max_records).data
        else:
            raise NotImplementedError("Type of StacEnum not implemented")
        return data
