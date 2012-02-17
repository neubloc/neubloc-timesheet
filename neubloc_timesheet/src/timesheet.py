#!/usr/bin/env python2

import signal
from gui import TimesheetUI

def run():
    app = TimesheetUI()
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app.run()


if __name__ == "__main__":
    run()
