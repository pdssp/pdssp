# -*- coding: utf-8 -*-
# Data Access Layer for PDSP - Provides the data access layer for accessing to the data from PDSP
# Copyright (C) 2021 - CNES (Jean-Christophe Malapert for Pôle Surfaces Planétaires)
#
# This file is part of Data Access Layer for PDSP.
#
# Data Access Layer for PDSP is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License v3  as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Data Access Layer for PDSP is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License v3  for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Data Access Layer for PDSP.  If not, see <https://www.gnu.org/licenses/>.
"""Project metadata."""
from pkg_resources import DistributionNotFound
from pkg_resources import get_distribution

__name_soft__ = "pdssp"
try:
    __version__ = get_distribution(__name_soft__).version
except DistributionNotFound:
    __version__ = "0.0.0"
__title__ = "Pôle de Données et Services Surfaces Planétaires"
__description__ = "Povides tools and services for PDSSP"
__url__ = "https://github.com/pole-surfaces-planetaires/pdssp"
__author__ = "Jean-Christophe Malapert"
__author_email__ = "jean-christophe.malapert@cnes.fr"
__license__ = "GNU Lesser General Public License v3"
__copyright__ = (
    "2021, CNES (Jean-Christophe Malapert for Pôle Surfaces Planétaires)"
)
