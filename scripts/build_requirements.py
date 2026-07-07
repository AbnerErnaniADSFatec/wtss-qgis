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

import csv
import distutils.core
from pathlib import Path

dist = distutils.core.run_setup("setup.py")



python_home = "python3"
command = f"{python_home} -m pip install "

file = open(Path('wtss_plugin') / 'requirements.txt','w')

for req in dist.install_requires:
	command += f'"{req}" '
	file.write(str(req) + "\n")

command += "--force-reinstall --no-cache --break-system-packages"

file.write(f"# {command}" + "\n")

file.close()

print("\n", command, "\n")
