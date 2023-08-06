SUN (Slackware Update Notifier)
===============================
Version 1.5.1 - (24/05/2023)
### Fixed
- SlackBuild script for repositories.toml file

Version 1.5.0 - (19/05/2023)
### Fixed
- Daemon notification message
### Added
- Configuration file /etc/sun/repositories.toml

Version 1.4.9 - (22/02/2023)
### BugFixed
- Time interval sleep

- Version 1.4.8 - (22/02/2023)
### Updated
- The daemon passed to the config file
- sun_daemon completed control with daemon tool
- sun_daemon works independently of sun check command
- The comparison of the logs passed to the repository section

Version 1.4.7 - (22/02/2023)
### Fixed
- Slackbuild script

Version 1.4.6 - (19/02/2023)
### Updated
- Error for http connection error
- Error for the Log file if not exists
- Increased the interval to 720 minutes
### Added
- Prefix to the config to check for in the Log files
### Fixed
- sun_daemon process in KDE env

Version 1.4.5 - (17/02/2023)
### Updated
- Support multi repositories
### Fixed
- f string in the config file

Version 1.4.4 - (14/02/2023)
### Updated
- For a Regular Expression Syntax

Version 1.4.3 - (06/02/2023)
### Added
- Packages pattern and kernel pattern in the config file
- Mirror and library in the config file

Version 1.4.2 - (23/12/2022)
### Updated
- Improve the code
- Dependencies (remove python-toml)

Version 1.4.1 - (08/12/2022)
### Updated
- Replace the bash autostart daemon script with python script

Version 1.4.0 - (06/12/2022)
### Updated
- Code style
- Daemon autostart scripts
### Fixed
- Function bash scripts

Version 1.3.9 - (05/12/2022)
### Updated
- Utilities to class object
- Metadata switch to dictionary

Version 1.3.8 - (03/12/2022)
### Fixed
- Restarting daemon message
### Added
- Some scripts for enable or disable daemon by the user (Thanks to marav) #12
- Check the subprocess output status
### Updated
- subprocess run once from cli either from gtk

Version 1.3.7 - (02/12/2022)
### Updated
- CLI menu
### Added
- Getting processor information
- Getting memory information
- Getting disk information
- Uptime information

Version 1.3.6 - (01/12/2022)
### Fixed
- Fixed stderr error output
- sun.conf is overwritten on reinstall #13
### Updated
- Switch sun configuration file with python toml
- Install sun.desktop in the /etc/xdg/autostart (Thanks to marav) #12
- Install sun_daemon.desktop in the /etc/xdg/autostart #12
- Add daemon tool to manage sun_daemon

Version 1.3.5 - (18/02/2022)
### Fixed
- Version in SlackBuild file

Version 1.3.4 - (18/02/2022)
### Updated
- For ftp mirrors

Version 1.3.3 - (16/02/2022)
### Updated
- Replace sun icon with new

Version 1.3.2 - *(09/02/2022)*
### Updated
- Copyright year
- Dependecies

Version 1.3.1 - *(03/04/2020)*
### Updated
- Temporary avoid working with ftp mirrors #9

Version 1.3.0 - *(12/02/2020)*
### Updated
- Migrate to Gtk 3.0
- Migrate to Python 3
### Added
- Testing with pytest

Version 1.2.3 - *(07/07/2018)*
### Updated
- Switch to gitlab repository

Version 1.2.2 - *(03/03/2018)*
### Updated
- Switch to python-notify2
### Fixed
- Added directories and removed packages

Version 1.2.1 - *(09/03/2016)*
### Fixed
- Start daemon when GTK icon loaded
### Updated
- Rename main.py to daemon.py 

Version 1.2.0 - *(08/03/2016)*
### Updated
- Management daemon without using rc.sun file. Thanks to Robby
Workman for the contribution #6

Version 1.1.7 - *(16/02/2016)*
### Fixed
- Avoid terminate gtk status icon

Version 1.1.6 - *(10/02/2016*)
### Added
- Keyboard interrupt on cli, daemon and gtk
### Fixed
- IOError: [Errno 2] No such file or directory: '/var/lib/slackpkg/ChangeLog.txt'

Version 1.1.5 - *(30/01/2016)*
### Updated
- Copyright 2015-2016
- Year int to string
### Fixed
- SUN status icon

Version 1.1.4 - *(07/09/2015)*
### Updated
- ChangeLog.txt url
### Removed
- sun mirrors file

Version 1.1.3 - *(11/8/2015)*
### Fixed
- setup.py install requirements

Version 1.1.2 - *(11/08/2015)*
### Added
- Support Slackware ARM

Version 1.1.1 - *(01/08/2015)*
### Fixed
- Support old Slackware versions
### Updated
- SlackBuild script

Version 1.1.0 - *(10/06/2015)*
### Added
- Preserve_perms to doinst.sh. Thanks to Thibaut Notteboom
- Submenu gtk icons
### Fixed
- Doc strings
- Tooltip message
- Merge added packages in count

Version 1.0.9 - *(15/05/2015)*
### Fixed
- Messages and added status icon message
### Updated
- CLI tool
### Added
- User name in info

Version 1.0.8 - *(23/04/2015)*
### Added
- Counted new packages added

Version 1.0.71 - *(16/04/2015)*
### Fixed
- License

Version 1.0.7 - *(15/04/2015)*
### Updated
- Merge license to about

Version 1.0.6 - *(31/03/2015)*
### Fixed
- Daemon loop wait one second before connect to ISP

Version 1.0.5 - *(20/03/2015)*
### Fixed
- Ignore current in information
### Updated
- Update CLI tool

Version 1.0.4 - *(18/03/2015)*
### Added
- Information, license and update gtk.MessageBox

Version 1.0.3 - *(14/03/2015)*
### Fixed
- BugFix with slackpkg+ update. Thanks to Maciej Gołuchowski for report
- BugFix gtk display large number of packages

Version 1.0.2 - *(14/03/2015)*
### Added
- Gtk status icon with popup menu

Version 1.0.1 - *(11/03/2015)*
### Updated
- CLI options
### Added
- Check software updates
- Display upgraded or rebuilt packages

Version 1.0.0 - *(04/03/2015)
### Added
- Released version 1.0.0
