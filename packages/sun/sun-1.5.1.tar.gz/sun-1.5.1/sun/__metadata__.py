#!/usr/bin/python3
# -*- coding: utf-8 -*-

# __metadata__.py is a part of sun.

# Copyright 2015-2023 Dimitris Zlatanidis <d.zlatanidis@gmail.com>
# All rights reserved.

# sun is a tray notification applet for informing about
# package updates in Slackware.

# https://gitlab.com/dslackw/sun

# sun is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


import os
import shutil
import platform
import subprocess
from pathlib import Path


__all__: str = 'sun'
__author__: str = 'dslackw'
__copyright__: str = '2015-2022'
__version_info__: tuple = (1, 5, 1)
__version__: str = '{0}.{1}.{2}'.format(*__version_info__)
__license__: str = 'GNU General Public License v3 (GPLv3)'
__email__: str = 'dslackw@gmail.com'
__website__: str = 'https://gitlab.com/dslackw/sun'


data_configs: dict = {
    'bin_path': Path('/usr/bin/'),
    'pkg_path': Path('/var/log/packages'),
    'icon_path': Path('/usr/share/pixmaps'),
    'desktop_path': Path('/usr/share/applications'),
    'xdg_autostart': Path('/etc/xdg/autostart'),
    'sun_conf_path': Path('/etc/', __all__),
    'arch': platform.machine(),
    'kernel': os.uname()[2],
    'cpu': platform.processor(),
    'mem': subprocess.getoutput('free -h').split(),
    'disk': shutil.disk_usage('/'),
    'uptime': subprocess.getoutput('uptime -p')
}
