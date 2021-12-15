# -*- coding: utf-8 -*-
from enum import Enum

from .mizar import Mizar


class PluginVisu(Enum):
    MIZAR = "mizar"


class Surface:
    @staticmethod
    def create_with(name: PluginVisu):
        plugin = None
        if name == PluginVisu.MIZAR:
            plugin = Mizar()
        else:
            raise NotImplementedError("Not implemented")
        return plugin
