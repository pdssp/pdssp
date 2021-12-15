# -*- coding: utf-8 -*-
import json
import logging
from abc import ABC
from dataclasses import dataclass
from typing import Dict
from typing import Optional

logger = logging.getLogger(__name__)


class ISurface(ABC):
    @classmethod
    def __subclasshook__(cls, subclass):
        """Check required method are well implemented in subclasses"""
        return (
            hasattr(subclass, "add_layer")
            and callable(subclass.add_layer)
            and hasattr(subclass, "remove_layer")
            and callable(subclass.remove_layer)
            and hasattr(subclass, "clear_layers")
            and callable(subclass.clear_layers)
            and hasattr(subclass, "zoom_to")
            and callable(subclass.zoom_to)
            and hasattr(subclass, "show")
            and callable(subclass.show)
            and hasattr(subclass, "highlight")
            and callable(subclass.highlight)
            or NotImplemented
        )

    def add_layer(self, layer):
        raise NotImplementedError("Not implemented")

    def remove_layer(self, rm_layer) -> bool:
        raise NotImplementedError("Not implemented")

    def clear_layers(self):
        raise NotImplementedError("Not implemented")

    def zoom_to(self, center, **kwargs):
        raise NotImplementedError("Not implemented")

    def show(self):
        raise NotImplementedError("Not implemented")

    def highlight(self, json_geometry=None, color=[1, 0, 0, 1]):
        raise NotImplementedError("Not implemented")


@dataclass
class GeoJSONLayer:
    name: str
    style: Optional[Dict] = None
    url: Optional[str] = None
    data: Optional[Dict] = None
    background: bool = True
    visible: bool = True
    opacity: float = 1.0


@dataclass
class WMSLayer:
    name: str
    url: str
    layers: str
    format: str
    background: bool = True
    visible: bool = True
    opacity: float = 1.0
    transparent: bool = False


@dataclass
class WMTSLayer:
    name: str
    url: str
    layers: str
    format: str
    background: bool = True
    visible: bool = True
    opacity: float = 1.0
    transparent: bool = False
