#
# This file is part of Python QGIS Plugin for WTSS.
# Copyright (C) 2024 INPE.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/gpl-3.0.html>.
#

"""Python QGIS Plugin for WTSS."""

import os
import sys
from pathlib import Path


class Config:
    """Base configuration for global variables.

    :attribute BASE_DIR(str): Returns app root path.
    """

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    STAC_HOST = os.getenv("STAC_HOST", "https://data.inpe.br/bdc/stac/v1/")

    WTSS_HOST = os.getenv("WTSS_HOST", "https://data.inpe.br/bdc/wtss/v4/")

    TEMPORARY_LAYER_NAME = os.getenv("TEMPORARY_LAYER_NAME", "wtss_coordinates_history")

    PYTHONPATH_WTSS_PLUGIN = os.getenv("PYTHONPATH_WTSS_PLUGIN", None)

    def __init__(self, file_path):
        self.file_path = file_path

    def lib_path(self):
        """Get the path for python installed lib path."""
        return str(Path(os.path.abspath(os.path.dirname(self.file_path))) / 'lib')

    def lib_path_end(self):
        """Get the path for python installed lib path."""
        return str(os.path.join(str(Path(os.path.abspath(os.path.dirname(self.file_path))) / 'lib'), ''))

    def get_lib_paths(self):
        """Get the path for python installed lib path."""
        return [self.lib_path(), self.lib_path_end()]

    def set_lib_path(self):
        """Setting lib path for installed libraries."""
        if self.lib_path() in sys.path:
            sys.path.remove(self.lib_path())
        if self.lib_path_end() in sys.path:
            sys.path.remove(self.lib_path_end())
        os.environ['PYTHONPATH_WLTS_PLUGIN'] = ':'.join(sys.path)
        sys.path = self.get_lib_paths() + sys.path
