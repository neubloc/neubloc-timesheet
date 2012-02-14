#!/usr/bin/env python2

import os, sys
import signal

## Gtk 2
#import Gtk
## Gtk 3
from gi.repository import Gtk, Gio, Gdk
Gdk.threads_init()


print os.getenv('DEBUG')

import time
from datetime import date, datetime, timedelta
from datetime import time as time2 

from timesheet import *
        
class TimesheetUI(Gtk.Application):

    def __init__(self):
        Gtk.Application.__init__(self, application_id="apps.test.helloworld", flags=Gio.ApplicationFlags.FLAGS_NONE)
        #self.connect("activate", self.on_activate)
        self.on_activate()

    ###  signal handlers
    def on_quit(self, widget, data=None):
        Gtk.main_quit()
     
    def on_activate(self, data=None):
        builder = Gtk.Builder()
        builder.add_from_file("gui.glade") 
        builder.connect_signals(self)       
        
        self.window = builder.get_object("window")
        self.window.show_all()

        # objects
        self.hourlist = builder.get_object("hourlist")
        self.hours = builder.get_object("hours")
        self.today_hours = builder.get_object("today")
        self.toggle_home = builder.get_object("client_home")
        self.toggle_neubloc = builder.get_object("client_neubloc")

        self.timesheet = Timesheet()       
        if self.timesheet.client == Actions.HOME:
            self.toggle_home.set_active(True)
        else:
            self.toggle_neubloc.set_active(True)

        self._reload()

    def on_start(self, action):
        self.timesheet.start()
        self._reload()

    def on_stop(self, action):
        self.timesheet.stop()
        self._reload()

    def on_toggle_client(self, button):
        button_name = Gtk.Buildable.get_name(button) 

        if(button_name == 'client_home'):
            v  = self.toggle_home.get_active()
            self.toggle_neubloc.set_active( (v+1)%2 )

            self.timesheet.client = Actions.HOME
            self.timesheet.actions = Actions.get(Actions.HOME)

        if(button_name == 'client_neubloc'):
            v  = self.toggle_neubloc.get_active()
            self.toggle_home.set_active( (v+1)%2 )

            self.timesheet.client = Actions.NEUBLOC
            self.timesheet.actions = Actions.get(Actions.NEUBLOC)

    ### private

    def _reload(self):
        hlist  = self.timesheet.list(datetime.now()) # - timedelta(days=2))

        self._today_hours(hlist)
        self._month_hours(hlist)
        self._hourlists(hlist)

    # coun today hourst
    def _today_hours(self, hlist):
        delta = timedelta(0)
        for h1,h2 in zip(hlist[::2],hlist[1::2]):
            t1 = h1[0]
            minute = -1 if t1.second >= 30 else 0
            t1 = (datetime.combine(date.today(), t1) - timedelta(minutes=minute, seconds=t1.second))

            t2 = h2[0]
            minute = -1 if t2.second >= 30 else 0
            t2 = (datetime.combine(date.today(), t2) - timedelta(minutes=minute, seconds=t2.second))

            delta += (t1 - t2)

        if len(hlist):
            delta += datetime.now() - datetime.combine(datetime.now(), hlist[-1][0]) 

        delta_h = delta.seconds/3600
        delta_m = delta.seconds/60 - delta_h*60
        delta_s = delta.seconds    - delta_h*3600 - delta_m*60
        delta = "%s:%s:%s" % (delta_h, delta_m, delta_s)        
        self.today_hours.set_text("Today hours:\n%s" % delta)

    # month hours bilans
    def _month_hours(self, hlist):
        self.hours.set_text("Month hours:\n%s" % self.timesheet.hours() ) 

    # formatting for list
    def _hourlists(self, hlist):
        hlist.reverse()
        hlist = ["%s / %s\n" % (h[0],h[1]) for h in hlist]
        hlist_str = "\n".join(h1+h2 for h1,h2 in zip(hlist[::2], hlist[1::2]))
        if len(hlist) % 2 == 1:
            hlist_str += hlist[-1]

        self.hourlist.set_text(hlist_str) 


class TimesheetDaylist(object):
    def __init__(self, container):
        self.container = container

class TimesheetSignals():
    pass


if __name__ == "__main__":
    app = TimesheetUI()

    #signal.signal(signal.SIGINT, app.quit)
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    Gtk.main()



