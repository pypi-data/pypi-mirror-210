#!/usr/bin/python3
# -*- coding: utf-8 -*-

# daemon.py is a part of sun.

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


"""
 ____  _   _ _   _
/ ___|| | | | \ | |
\___ \| | | |  \| |
 ___) | |_| | |\  |
|____/ \___/|_| \_|

"""

import time
import notify2

from sun.cli.tool import Tools
from sun.configs import Configs
from sun.utils import Fetch
from sun.__metadata__ import __all__, data_configs


class Notify(Configs):
    """ Main notify Class. """

    def __init__(self):
        super(Configs, self).__init__()
        self.tool = Tools()
        self.fetch = Fetch()

        self.notify = None
        self.icon = None
        self.message: str = str()
        self.count_packages: int = 0
        self.title: str = f"{'':>10}Software Updates"
        self.icon: str = f'{data_configs["icon_path"]}/{__all__}.png'

        notify2.uninit()
        notify2.init('sun')

    def set_notification_message(self):
        self.count_packages: int = len(list(self.fetch.updates()))
        self.message: str = f"{'':>3}{self.count_packages} Software updates are available\n"
        self.notify = notify2.Notification(self.title, self.message, self.icon)
        self.notify.set_timeout(60000 * self.standby)

    def daemon(self) -> None:
        """ SUN daemon. """
        while True:
            self.set_notification_message()
            if self.count_packages > 0:
                self.notify.show()

            time.sleep(60 * self.interval)
