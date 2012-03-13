#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os, signal
import subprocess, shlex
import setproctitle
from gui import TimesheetUI

def run():
    setproctitle.setproctitle('neubloc_timesheet')

    app = TimesheetUI()
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app.run()

def install_icons():
    cd = os.path.dirname(os.path.abspath(__file__))

    cmd = '''\
sudo cp {0}/static/neubloc-timesheet.png /usr/share/pixmaps/
sudo cp {0}/static/neubloc-timesheet-debug.png /usr/share/pixmaps/
sudo gtk-update-icon-cache\
'''.format(cd)

    for line in cmd.split("\n"):
        print line
        subprocess.Popen(shlex.split(line))

    print "\n.. done"


if __name__ == "__main__":
    run()
