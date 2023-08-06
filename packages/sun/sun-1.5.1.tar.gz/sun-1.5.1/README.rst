.. contents:: Table of Contents:

About
-----

Let's SUN!


SUN (Slackware Update Notifier) is a tray notification applet for informing about
package updates in Slackware and CLI tool for monitoring upgraded packages.

.. image:: https://gitlab.com/dslackw/images/raw/master/sun/sun.png
    :target: https://gitlab.com/dslackw/sun

How works
---------

SUN compares the two dates of ChangeLog.txt files on the server and locally by counting
how many packages have been upgraded, rebuilt or added etc.

SUN works with `slackpkg <http://www.slackpkg.org/>`_ as well as with others tools and repositories.
Probably, you can use the SUN with other's Slackware based Linux distributions as well.
 

Installing
----------

.. code-block:: bash

    Required root privileges

    $ tar xvf sun-1.5.1.tar.gz
    $ cd sun-1.5.1
    $ ./install.sh

    Installed as Slackware package


Usage
-----

| Edit the configuration :code:`/etc/sun/repositories.toml` file and change a http mirror for your country.
| NOTE: ftp mirrors not supported.


GTK Icon
--------

.. image:: https://gitlab.com/dslackw/images/raw/master/sun/gtk_daemon.png
   :target: https://gitlab.com/dslackw/sun

.. image:: https://gitlab.com/dslackw/images/raw/master/sun/check_updates.png
   :target: https://gitlab.com/dslackw/sun

.. image:: https://gitlab.com/dslackw/images/raw/master/sun/sun_running.png
   :target: https://gitlab.com/dslackw/sun

CLI
---

.. code-block:: bash

    $ sun help
    SUN (Slackware Update Notifier) - Version: 1.5.1

    Usage: sun [OPTIONS]

    Optional arguments:
      help       Display this help and exit.
      start      Start sun daemon.
      stop       Stop sun daemon.
      restart    Restart sun daemon.
      check      Check for software updates.
      status     Sun daemon status.
      info       Os information.

    Start GTK icon from the terminal: sun start --gtk


    $ sun start
    Starting SUN daemon:  /usr/bin/sun_daemon &

    $ sun check
    3 software updates are available from 1 repository

    Slack: samba-4.1.17-x86_64-1_slack14.1.txz
    Slack: mozilla-firefox-31.5.1esr-x86_64-1_slack14.1.txz
    Slack: mozilla-thunderbird-31.5.1-x86_64-1_slack14.1.txz

    $ sun stop
    Stopping SUN daemon:  /usr/bin/sun_daemon

    $ sun status
    SUN is not running


Daemon autostart
----------------

.. code-block:: bash

    If you want sun daemon to autostart automatically in every boot, run as root:

    $ sun_daemon enable

    or for disable the autostart sun daemon:

    $ sun_daemon disable

    for help

    $ sun_daemon help

KDE Environment
---------------

| For KDE users, they may need to copy the :code:`sun.desktop` file into :code:`$HOME/.config/autostart` folder.
| About autostart KDE manager, please visit `here <https://docs.kde.org/trunk5/en/plasma-workspace/kcontrol/autostart/autostart.pdf>`_.


Configuration files
-------------------

.. code-block:: bash

    /etc/sun/sun.toml
        General configuration of sun

    /etc/sun/repositories.toml
        Repositories configuration of sun


Donate
------

If you feel satisfied with this project and want to thank me, treat me to a coffee ☕ !

.. image:: https://gitlab.com/dslackw/images/raw/master/donate/paypaldonate.png
   :target: https://www.paypal.me/dslackw


Copyright
---------

- Copyright 2015-2023 © Dimitris Zlatanidis
- Slackware® is a Registered Trademark of Patrick Volkerding.
- Linux is a Registered Trademark of Linus Torvalds.
