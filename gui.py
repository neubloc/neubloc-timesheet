#!/usr/bin/env python2

import vimpdb
import os, sys
import signal
import pdb
from threading import Thread

## Gtk 2
#import Gtk
## Gtk 3
from gi.repository import Gtk, Gio, Gdk, GLib

DEBUG = bool(os.getenv('DEBUG'))

import time
from datetime import date, datetime, timedelta
from datetime import time as time2 

from timesheet import *
        
class TimesheetUI(Gtk.Application):

    hlist = []

    def __init__(self):
        Gtk.Application.__init__(self, application_id="apps.test.helloworld", flags=Gio.ApplicationFlags.FLAGS_NONE)
        #self.connect("activate", self.on_activate)
        self.on_activate()

        #Thread(target=self.count, args=(maximum,)).start()
        self.today_hours_thr = Thread(target=self._today_hours_thread).start()

        #vimpdb.set_trace()

    ###  signal handlers
    def on_quit(self, widget, data=None):
        self._toggle_visibility()
        return True
     
    def on_activate(self, data=None):
        builder = Gtk.Builder()
        builder.add_from_file("gui.glade") 
        builder.connect_signals(self)       

        # status icon
        self.statusIcon = Gtk.StatusIcon()
        self.statusIcon.set_from_file("%s" % 'icon.png')
        self.statusIcon.set_visible(True)
        self.statusIcon.connect("activate", self.on_icon_activated)
        self.statusIcon.connect("popup-menu", self.on_icon_popup)

        
        self.window = builder.get_object("window")
        self.window.show_all()

        # objects
        self.hourlist = builder.get_object("hourlist")
        self.hours = builder.get_object("hours")
        self.today_hours = builder.get_object("today")
        self.toggle_home = builder.get_object("client_home")
        self.toggle_neubloc = builder.get_object("client_neubloc")

        self.start = builder.get_object("start")
        self.stop= builder.get_object("stop")
        #self.start.set_sensitive(False)

        self.timesheet = Timesheet()       
        if self.timesheet.client == Actions.HOME:
            self.toggle_home.set_active(True)
        else:
            self.toggle_neubloc.set_active(True)

        self._reload()

    def on_start(self, action):
        Thread(target=self._on_start).start()

    def _on_start(self):
        self.timesheet.start()
        self._reload()

    def on_stop(self, action):
        Thread(target=self._on_stop).start()

    def _on_stop(self):
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

    def on_icon_activated(self, data=None):
        self._toggle_visibility()

    def on_icon_popup(self, data, arg1, arg2):
        self._quit()


    ### private

    def _toggle_visibility(self):
        if self.window.get_visible():
            self.window.hide_on_delete()
        else:
            self.window.show_all()

    def _quit(self):
        self.window.hide()
        Gtk.main_quit()
        signal.alarm(signal.SIGINT)

    def _reload(self):
        if DEBUG:
            hlist = [
             (datetime(1,1,1,19, 00, 11).time(), u'DK (Start Dom)'), 
             (datetime(1,1,1,10, 46, 11).time(), u'DK (Koniec Dom)'), 
             (datetime(1,1,1,8, 34, 58).time(), u'DS (Start Dom)')
            ]
        else:
            hlist  = self.timesheet.list(datetime.now()) # - timedelta(days=2))

        hlist.reverse()
        self.hlist = hlist

        self._today_hours(hlist)
        self._month_hours(hlist)
        self._hourlists(hlist)

    # coun today hourst
    def _today_hours(self, hlist=None):
        if hlist == None: hlist = self.hlist

        delta = timedelta(0)
        for h1,h2 in zip(hlist[::2],hlist[1::2]):
            t1 = h1[0]
            minute = -1 if t1.second >= 30 else 0
            t1 = (datetime.combine(date.today(), t1) - timedelta(minutes=minute, seconds=t1.second))

            t2 = h2[0]
            minute = -1 if t2.second >= 30 else 0
            t2 = (datetime.combine(date.today(), t2) - timedelta(minutes=minute, seconds=t2.second))

            delta += (t2 - t1)

        if len(hlist) % 2 == 1:
            delta += datetime.now() - datetime.combine(datetime.now(), hlist[-1][0]) 

        # time remaining
        try:
            rdelta = self._timedelta_to_string(timedelta(hours=8) - delta)
        except OverflowError:
            rdelta = timedelta(0)

        # time passed
        delta = self._timedelta_to_string(delta)

        self.today_hours.set_text("""
Today hours:
Passed: 
%(passed)s
Remaining: 
%(remaining)s
""" % {'passed': delta, 'remaining': rdelta}
        )

    def _today_hours_thread(self):
        while True:
            self._today_hours()
            time.sleep(1)

    def _timedelta_to_string(self, delta):
        delta_h = delta.seconds/3600
        delta_m = delta.seconds/60 - delta_h*60
        delta_s = delta.seconds    - delta_h*3600 - delta_m*60
        return "%d:%.2d:%.2d" % (delta_h, delta_m, delta_s)        

    # month hours bilans
    def _month_hours(self, hlist):
        self.hours.set_text("Month hours:\n%s" % self.timesheet.hours() ) 

    # formatting for list
    def _hourlists(self, hlist):
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

    #signal.signal(signal.SIGINT, app.on_quit)
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    GLib.threads_init()
    Gdk.threads_enter()
    Gtk.main()
    Gdk.threads_leave()



