#!/bin/sh
# Pôle de Données et Services Surfaces Planétaires - Provides tools and services for PDSSP
# Copyright (C) 2021 - CNES (Jean-Christophe Malapert for Pôle Surfaces Planétaires)
#
# This file is part of Pôle de Données et Services Surfaces Planétaires.
#
# Pôle de Données et Services Surfaces Planétaires is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pôle de Données et Services Surfaces Planétaires is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pôle de Données et Services Surfaces Planétaires.  If not, see <https://www.gnu.org/licenses/>.
docker build --no-cache=true --build-arg SSH_PRIVATE_KEY="`more ~/.ssh/id_rsa`" -t dev/pdssp .
