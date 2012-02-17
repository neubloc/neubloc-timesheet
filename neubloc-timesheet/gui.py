#!/usr/bin/env python2

import vimpdb
import os, sys
import signal
import time
from threading import Thread
from datetime import date, datetime, timedelta
from datetime import time as time2 

from gi.repository import Gtk, Gio, Gdk, GLib

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/lib')

from lib.timesheet import *
from lib.config import *

DEBUG = bool(os.getenv('DEBUG'))
COLORS = { 'green': "#33af95ac3c98", 'red': "#ffff587b587b" }

class TimesheetUI(Gtk.Application):
    """
        Gtk3 app for Timesheet lib
    """
    hlist = []

    def __init__(self):
        Gtk.Application.__init__(self, application_id="apps.test.helloworld", flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.on_activate()

        # threads
        self.today_hours_thr = Thread(target=self._today_hours_thread).start()

    ###  signal handlers
    def on_quit(self, widget, data=None):
        self._toggle_visibility()
        return True
     
    def on_activate(self, data=None):
        builder = Gtk.Builder()
        builder.add_from_file("static/gui.glade") 
        builder.connect_signals(self)       

        # status icon
        self.status_icon = Gtk.StatusIcon()
        self.status_icon.set_from_file("%s" % 'static/icon.png')
        self.status_icon.set_visible(True)
        self.status_icon.connect("activate", self.on_icon_activated)
        self.status_icon.connect("popup-menu", self.on_icon_popup)

        # objects
        self.hourlist = builder.get_object("hourlist")
        self.hours = builder.get_object("hours")
        self.today_hours = builder.get_object("today")
        self.toggle_home = builder.get_object("client_home")
        self.toggle_neubloc = builder.get_object("client_neubloc")

        self.start = builder.get_object("start")
        self.stop= builder.get_object("stop")
        #self.start.set_sensitive(False)

        self.model = builder.get_object("hourlist_store")
        self.list = builder.get_object("hourlist_view")

        self.config = Config()
        self.timesheet = Timesheet(self.config.get_user(), self.config.get_client())       
        if self.timesheet.client == Actions.HOME:
            self.toggle_home.set_active(True)
        else:
            self.toggle_neubloc.set_active(True)

        self._reload()

        self.window = builder.get_object("window")
        if self.config.get_minimized() == False:
            self.window.show_all()

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

            self.config.set_client('home')

        if(button_name == 'client_neubloc'):
            v  = self.toggle_neubloc.get_active()
            self.toggle_home.set_active( (v+1)%2 )

            self.timesheet.client = Actions.NEUBLOC
            self.timesheet.actions = Actions.get(Actions.NEUBLOC)

        self.config.set_client(self.timesheet.client)

    def on_icon_activated(self, data=None):
        self._toggle_visibility()

    def on_icon_popup(self, data, arg1, arg2):
        self._quit()

    def on_window_state(self, window, event):
        #if event.new_window_state == Gdk.WindowState.ICONIFIED:
        #    self._toggle_visibility()
        pass

    ### private
    def _toggle_visibility(self):

        self.config.set_minimized(self.window.get_visible())
        if self.window.get_visible():
            self.window.hide() #_on_delete()
        else:
            self.window.show_all()


    def _quit(self):
        self.window.hide()
        Gtk.main_quit()
        signal.alarm(1)

    def _reload(self):
        if DEBUG:
            hlist = [
             (datetime(1,1,1,19, 00, 11).time(), 'OS (Start Dom)'), 
             (datetime(1,1,1,10, 46, 11).time(), 'DK (Koniec Dom)'), 
             (datetime(1,1,1,8, 34, 58).time(), 'DS (Start Dom)')
            ]
        else:
            hlist  = self.timesheet.list(datetime.now()) # - timedelta(days=2))

        hlist.reverse()
        self.hlist = hlist

        self._today_hours(hlist)
        self._month_hours(hlist)
        self._hourlists(hlist)

    # coun today hours
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

        data = """Passed:\n<b>%(passed)s</b>\nRemaining:\n<b>%(remaining)s</b>""" % {'passed': delta, 'remaining': rdelta}

        self.today_hours.set_markup(data)
        self.status_icon.set_tooltip_markup(data)

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
        hours = self.timesheet.hours()
        color = COLORS['red'] if hours[0] == '-' else COLORS['green']
        self.hours.set_markup("<span color='%s'>%s</span>" % (color, hours[1:]) ) 

    # formatting for list
    def _hourlists(self, hlist):
        for h in hlist:
            time = str(h[0])
            type = h[1][:2]
            color = COLORS['red'] if type[1] == "K" else COLORS['green']

            self.model.append([time, Actions.ext[type], color])


if __name__ == "__main__":
    app = TimesheetUI()

    #signal.signal(signal.SIGINT, app.on_quit)
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    GLib.threads_init()
    Gdk.threads_enter()
    Gtk.main()
    Gdk.threads_leave()



