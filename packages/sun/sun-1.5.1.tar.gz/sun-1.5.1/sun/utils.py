#!/usr/bin/python3
# -*- coding: utf-8 -*-

# utils.py is a part of sun.

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


import re
import getpass
import urllib3
import requests
from typing import Generator
from pathlib import Path
from sun.configs import Configs
from sun.__metadata__ import data_configs


class Utilities(Configs):
    """ General utilities. """

    def __init__(self):
        super(Configs, self).__init__()
        self.data_configs: dict = data_configs

    @staticmethod
    def read_repo_text_file(mirror: str) -> str:
        """ Reads and returns the mirror log text files. """
        log_txt: str = str()
        try:
            requests.get(mirror, timeout=2)
            http = urllib3.PoolManager()
            con = http.request('GET', mirror)
            log_txt = con.data.decode()
        except KeyError:
            print('SUN: error: ftp mirror not supported')
        except requests.exceptions.RequestException:
            print(f'Error: Failed to connect to {mirror}')

        return log_txt

    @staticmethod
    def read_local_text_file(registry: Path) -> str:
        """ Reads and returns the local log text files. """
        log_txt: str = str()
        if registry.is_file():
            with open(registry, 'r', encoding='utf-8', errors='ignore') as file_txt:
                log_txt = file_txt.read()
        else:
            print(f"\nError: Failed to find '{registry}' file.\n")

        return log_txt

    def slack_version(self) -> tuple:
        """ Returns the distribution name and version. """
        version_file: str = self.read_local_text_file(Path('/etc/slackware-version'))
        slackware_version: list = re.findall(r'\d+\.\d+', version_file)

        return version_file.split()[0], ''.join(slackware_version)

    def os_info(self) -> str:
        """ Returns the distribution information. """
        distribution: tuple = self.slack_version()
        os_name: str = distribution[0]
        version: str = distribution[1]
        return (f'User: {getpass.getuser()}\n'
                f'OS: {os_name}\n'
                f'Version: {version}\n'
                f'Arch: {self.data_configs["arch"]}\n'
                f'Packages: {len(list(self.data_configs["pkg_path"].iterdir()))}\n'
                f'Kernel: {self.data_configs["kernel"]}\n'
                f'Uptime: {self.data_configs["uptime"]}\n'
                '[Memory]\n'
                f'Free: {self.data_configs["mem"][9]}, Used: {self.data_configs["mem"][8]}, '
                f'Total: {self.data_configs["mem"][7]}\n'
                '[Disk]\n'
                f'Free: {self.data_configs["disk"][2] // (2**30)}Gi, Used: '
                f'{self.data_configs["disk"][1] // (2**30)}Gi, '
                f'Total: {self.data_configs["disk"][0] // (2**30)}Gi\n'
                f'[Processor]\n'
                f'CPU: {self.data_configs["cpu"]}')


class Fetch(Utilities):
    """ Fetching how many packages and from where have upgraded,
        removed or added. """

    def __init__(self):
        super(Utilities).__init__()
        self.local_date = None
        self.repo_name = None
        self.repo_mirror = None
        self.repo_log_path = None
        self.repo_log_file = None
        self.repo_pattern = None
        self.repo_compare = None
        self.mirror_log = None
        self.local_log = None

    def updates(self) -> Generator:
        """ Fetching all the necessary packages. """
        for repository in self.repositories:
            self.assign_repository_data(repository)

            if self.repo_mirror and self.repo_log_path:
                self.assign_mirror_log_file()
                self.assign_local_log_file()
                self.assign_local_date()

                for line in self.mirror_log.splitlines():
                    if self.local_date == line.strip():
                        break
                    if re.findall(self.repo_pattern, line):
                        line: str = self.patch_line_for_slackware(line)
                        yield f'{self.repo_name}: {line.split("/")[-1]}'

    def assign_repository_data(self, repository: dict) -> None:
        """ Assign the repositories data from the .toml file. """
        try:
            self.repo_name: str = repository['REPOSITORY_NAME']
            self.repo_mirror: str = repository['HTTP_MIRROR']
            self.repo_log_path: str = repository['LOG_PATH']
            self.repo_log_file: str = repository['LOG_FILE']
            self.repo_pattern: str = repository['PACKAGE_PATTERN']
            self.repo_compare: str = repository['COMPARE_PATTERN']
        except KeyError as error:
            print(f"KeyError: {error}: in the config file '{self.config_path}{self.config_file}'.")

    def patch_line_for_slackware(self, line: str) -> str:
        """ Patches the line for linux updates. """
        slack_name: tuple = ('Slackware', 'slackware', 'Slack', 'slack')
        if line.startswith('patches/packages/linux') and self.repo_name in slack_name:
            line = line.split("/")[-2]
        return line

    def assign_local_date(self) -> None:
        """ Finds the date from the local log file and assigned. """
        for line in self.local_log.splitlines():
            if re.findall(self.repo_compare, line):
                self.local_date: str = line.strip()
                break

    def assign_mirror_log_file(self) -> None:
        """ Reads the mirror log file and assigned. """
        self.mirror_log: str = self.read_repo_text_file(f'{self.repo_mirror}{self.repo_log_file}')

    def assign_local_log_file(self) -> None:
        """ Reads the local log file and assigned. """
        self.local_log: str = self.read_local_text_file(Path(self.repo_log_path, self.repo_log_file))
        if not self.local_log:
            self.local_date: str = str()
