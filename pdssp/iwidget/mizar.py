# -*- coding: utf-8 -*-
from typing import cast
from typing import Dict
from typing import List
from typing import Union

import geopandas as gpd
import ipymizar

from .interface import GeoJSONLayer
from .interface import ISurface
from .interface import WMSLayer
from .interface import WMTSLayer

JSON = Union[None, bool, str, float, int, List["JSON"], Dict[str, "JSON"]]


class _MizarLayerFactory:
    @staticmethod
    def create(layer: Union[WMSLayer, GeoJSONLayer, WMTSLayer]):
        ipymizar_layer: Union[WMSLayer, GeoJSONLayer, WMTSLayer]
        if isinstance(layer, WMSLayer):
            ipymizar_layer = ipymizar.WMSLayer(
                name=layer.name,
                url=layer.url,
                layers=layer.layers,
                format=layer.format,
                background=layer.background,
                visible=layer.visible,
                opacity=layer.opacity,
                transparent=layer.transparent,
            )
        elif isinstance(layer, WMTSLayer):
            ipymizar_layer = ipymizar.WMTSLayer(
                name=layer.name,
                url=layer.url,
                layers=layer.layers,
                format=layer.format,
                background=layer.background,
                visible=layer.visible,
                opacity=layer.opacity,
                transparent=layer.transparent,
            )
        elif isinstance(layer, GeoJSONLayer):
            style_mizar: Dict
            if layer.style is None:
                style_mizar = {"strokeColor": [0, 190, 100, 1], "opacity": 1}
            else:
                style_mizar = layer.style
            if layer.url is not None:
                ipymizar_layer = ipymizar.GeoJSONLayer(
                    name=layer.name,
                    url=layer.url,
                    style=style_mizar,
                    background=layer.background,
                    visible=layer.visible,
                    opacity=layer.opacity,
                )
            elif layer.data is not None:
                ipymizar_layer = ipymizar.GeoJSONLayer(
                    name=layer.name,
                    data=layer.data,
                    style=style_mizar,
                    background=layer.background,
                    visible=layer.visible,
                    opacity=layer.opacity,
                )
            else:
                raise NotImplementedError(
                    "data or url are mandatories in GeoJsonLayer"
                )
        else:
            raise NotImplementedError("Layer not implemented")
        return ipymizar_layer


class Mizar(ISurface):
    def __init__(self):
        self.planet: ipymizar.MizarMap = ipymizar.MizarMap(
            crs=ipymizar.CRS.WGS84
        )
        self._is_highlight: bool = False

    def _computer_center_and_zoom(
        self, layer: Union[WMSLayer, GeoJSONLayer, WMTSLayer], center: bool
    ) -> None:
        if center is False or not isinstance(layer, GeoJSONLayer):
            return

        geojson_layer: GeoJSONLayer = layer
        data: Dict = cast(Dict, geojson_layer.data)
        gdf: gpd.GeoDataFrame = gpd.GeoDataFrame.from_features(
            data["features"]
        )
        min_lon, min_lat, max_lon, max_lat = gdf.total_bounds
        center_lat: float = 0.5 * (min_lat + max_lat)

        if (max_lon - min_lon) > 180:
            center_lon = 0.5 * (min_lon + 360 - max_lon) + max_lon
        else:
            center_lon: float = 0.5 * (min_lon + max_lon)

        self.zoom_to([center_lon, center_lat])

    def add_layer(
        self,
        layer: Union[WMSLayer, GeoJSONLayer, WMTSLayer],
        center: bool = False,
    ) -> None:
        layer_to_add: Union[WMSLayer, GeoJSONLayer, WMTSLayer]
        layer_to_add = _MizarLayerFactory.create(layer)
        self.planet.add_layer(layer_to_add)
        self._computer_center_and_zoom(layer, center)

    def remove_layer(self, layer_name) -> bool:
        is_removed: bool
        layer_find = None
        for layer in self.planet.layers:
            if layer.name == layer_name:
                layer_find = layer
                break

        if layer_find is None:
            is_removed = False
            print(f"Cannot find {layer_name}")
        else:
            is_removed = True
            self.planet.remove_layer(layer_find)
        return is_removed

    def clear_layers(self) -> None:
        self.planet.clear_layers()

    def zoom_to(self, center, **kwargs) -> None:
        self.planet.zoom_to(center, **kwargs)

    def show(self) -> ipymizar.MizarMap:
        return self.planet

    def highlight(self, json_geometry=None, color=[1, 0, 0, 1]) -> None:
        if self._is_highlight:
            self.remove_layer("highlight")
            self._is_highlight = False

        if json_geometry is not None:
            geojson = GeoJSONLayer(
                name="highlight",
                data=json_geometry,
                style={"strokeColor": color, "strokeWidth": 5, "zIndex": 31},
            )
            self.add_layer(geojson)
            self._is_highlight = True
