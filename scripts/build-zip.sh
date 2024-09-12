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
#!/bin/bash

LIB_PATH="./wtss_plugin/controller/lib"
SCRIPTS_PATH="./scripts"

mkdir -p ./wtss_plugin/controller/lib

cat $SCRIPTS_PATH/lib-paths.txt | while read path || [[ -n $path ]];
do
    echo "Copying all dependencies for "$path" to "$LIB_PATH
    cp -R $path ./wtss_plugin/controller/lib
done

cd wtss_plugin

pb_tool zip
