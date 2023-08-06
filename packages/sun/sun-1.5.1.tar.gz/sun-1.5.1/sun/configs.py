#!/usr/bin/python3
# -*- coding: utf-8 -*-

# configs.py is a part of sun.

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


import tomli
from pathlib import Path
from sun.__metadata__ import data_configs, __all__


class Configs:

    # Configuration files.
    config_file: str = f'{__all__}.toml'
    repositories_file: str = 'repositories.toml'
    config_path: str = data_configs['sun_conf_path']
    slpkg_toml: Path = Path(config_path, config_file)
    repositories_toml: Path = Path(config_path, repositories_file)
    configs: dict = {}
    repos: dict = {}

    # Default time configs.
    interval: int = 720
    standby: int = 3

    # Daemon default commands.
    sun_daemon_start: str = 'daemon -rB --pidfiles=~/.run --name=sun_daemon sun_daemon'
    sun_daemon_stop: str = 'daemon --pidfiles=~/.run --name=sun_daemon --stop'
    sun_daemon_restart: str = 'daemon --pidfiles=~/.run --name=sun_daemon --restart'
    sun_daemon_running: str = 'daemon --pidfiles=~/.run --name=sun_daemon --running'

    # Default repository
    repositories: list = [
        {'NAME': 'Slackware',
         'HTTP_MIRROR': 'https://mirrors.slackware.com/slackware/slackware64-15.0/',
         'LOG_PATH': '/var/lib/slackpkg/', 'LOG_FILE': 'ChangeLog.txt',
         'PATTERN': 'Upgraded[.]|Rebuilt[.]|Added[.]|Removed[.]',
         'COMPARE': '^\w[Mon|Tue|Wed|Thu|Fri|Sat|Sun]'}
    ]

    try:
        if slpkg_toml.is_file():
            with open(slpkg_toml, 'rb') as conf:
                configs: dict = tomli.load(conf)
        else:
            raise Exception(f"Error: Failed to find '{slpkg_toml}' file.")

        if repositories_toml.is_file():
            with open(repositories_toml, 'rb') as conf:
                repos: dict = tomli.load(conf)
        else:
            raise Exception(f"Error: Failed to find '{repositories_toml}' file.")

        # Time configs.
        interval: int = configs['time']['INTERVAL']
        standby: int = configs['time']['STANDBY']
        # Daemon configs.
        sun_daemon_start: str = configs['daemon']['START']
        sun_daemon_stop: str = configs['daemon']['STOP']
        sun_daemon_restart: str = configs['daemon']['RESTART']
        sun_daemon_running: str = configs['daemon']['RUNNING']
        # Repositories configs.
        repositories: list = repos['repository']

    except (tomli.TOMLDecodeError, KeyError) as error:
        raise SystemExit(f"Error: {error}: in the config file '{config_path}{config_file}'.")
