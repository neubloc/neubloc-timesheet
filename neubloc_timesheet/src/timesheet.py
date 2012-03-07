#!/usr/bin/env python2

import signal
import procname
from gui import TimesheetUI

def run():

    procname.setprocname('neubloc_timesheet')

    app = TimesheetUI()
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app.run()


if __name__ == "__main__":
    run()
