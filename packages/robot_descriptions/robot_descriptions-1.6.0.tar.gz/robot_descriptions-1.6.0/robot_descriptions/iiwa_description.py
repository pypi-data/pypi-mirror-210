#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2022 Stéphane Caron
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""iiwa 14 description."""

from os import getenv as _getenv
from os import path as _path

from ._cache import clone_to_cache as _clone_to_cache

REPOSITORY_PATH: str = _clone_to_cache(
    "drake",
    commit=_getenv("ROBOT_DESCRIPTION_COMMIT", None),
)

PACKAGE_PATH: str = _path.join(
    REPOSITORY_PATH, "manipulation", "models", "iiwa_description"
)

URDF_PATH: str = _path.join(
    PACKAGE_PATH, "urdf", "iiwa14_primitive_collision.urdf"
)

# Description-specific paths

URDF_PATH_NO_COLLISION: str = _path.join(
    PACKAGE_PATH, "urdf", "iiwa14_no_collision.urdf"
)

URDF_PATH_POLYTOPE_COLLISION: str = _path.join(
    PACKAGE_PATH, "urdf", "iiwa14_polytope_collision.urdf"
)

URDF_PATH_PRIMITIVE_COLLISION: str = _path.join(
    PACKAGE_PATH, "urdf", "iiwa14_primitive_collision.urdf"
)
