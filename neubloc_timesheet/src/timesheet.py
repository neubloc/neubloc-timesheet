#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import signal
import setproctitle
from gui import TimesheetUI

def run():

    setproctitle.setproctitle('neubloc_timesheet')

    app = TimesheetUI()
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app.run()


if __name__ == "__main__":
    run()
