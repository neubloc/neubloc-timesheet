#!/usr/bin/env python2

import os, sys
import time
import signal
from datetime import datetime, timedelta

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gtk, Gio, Gdk, GObject

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/lib')

from lib.timesheet import *
from lib.config import *

from decorators import threaded 

DEBUG = bool(os.getenv('DEBUG'))
COLORS = { 'green': "#33af95ac3c98", 'red': "#ffff587b587b" }

class TimesheetUI(Gtk.Application):
    """
        Gtk3 app for Timesheet lib
    """

    def __init__(self):
        Gtk.Application.__init__(self, 
                application_id="apps.neubloc.timesheet", 
                flags=Gio.ApplicationFlags.FLAGS_NONE)

        self.objects_assign()
        #self.statusbar_init()
        self.modules_init()
        self.actionbuttons_init()

        if self.config.get_minimized() == False:
            self._toggle_visibility()
        self.window.set_keep_above(True)

        # threads
        self._reload()
        self.today_hours_thr = self._today_hours_thread()

    def run(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # status icon
        try:
            from gi.repository import AppIndicator3 as appindicator
            ind = appindicator.Indicator.new ( "neubloc_timesheet", "indicator-messages", appindicator.IndicatorCategory.APPLICATION_STATUS)
            ind.set_status (appindicator.IndicatorStatus.ACTIVE)
            ind.set_attention_icon ("indicator-messages")

            menu = Gtk.Menu()
            item = Gtk.MenuItem("Empty")
            item.show()
            menu.append(item)
            ind.set_menu(menu)
        except ImportError:
            self.status_icon = Gtk.StatusIcon()
            self.status_icon.set_from_file( os.path.join(current_dir, 'static/icon.png'))
            if DEBUG:
                self.status_icon.set_from_file( os.path.join(current_dir, 'static/icon_debug.png'))
            self.status_icon.set_visible(True)
            self.status_icon.connect("activate", self.on_icon_activated)
            self.status_icon.connect("popup-menu", self.on_icon_popup)

        GObject.threads_init()
        Gdk.threads_enter()
        Gtk.main()
        Gdk.threads_leave()
     
    def objects_assign(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))

        builder = Gtk.Builder()
        builder.add_from_file("%s%s" % (current_dir, "/static/gui.glade")) 
        builder.connect_signals(self)       

        # objects
        self.hourlist = builder.get_object("hourlist")
        self.hours = builder.get_object("hours")
        self.today_hours = builder.get_object("today")
        self.toggle_home = builder.get_object("client_home")
        self.toggle_neubloc = builder.get_object("client_neubloc")

        self.today_passed = builder.get_object("today_passed")
        self.today_remaining = builder.get_object("today_remaining")

        self.start = builder.get_object("start")
        self.stop= builder.get_object("stop")

        self.hours_model = builder.get_object("hourlist_store")
        self.hours_list = builder.get_object("hourlist_view")

        self.days_model = builder.get_object("days_store")
        self.days_list = builder.get_object("days_view")
        self.days_selection = builder.get_object('days_selection')

        self.statusbar = builder.get_object("statusbar")

        self.project_choose_box = builder.get_object("project_choose_box")
        self.window = builder.get_object("window")


    def statusbar_init(self):
        #context_id = self.statusbar.get_context_id("context1")
        #self.statusbar.push(context_id, "..")
        pass

    def modules_init(self):
        self.config = Config()
        self.timesheet = Timesheet(self.config.get_user(), 
                                   self.config.get_client())       

    def actionbuttons_init(self):
        if self.timesheet.client == Actions.HOME:
            self.toggle_home.set_active(True)
        else:
            self.toggle_neubloc.set_active(True)

        #project choose
        self.project_buttons = []
        for name, ids in self.config.get_projects().items():
            group = self.project_buttons[0] if len(self.project_buttons) else None
            radio = Gtk.RadioButton("%s" % name, group=group)

            self.project_choose_box.pack_start(radio, True, True, 0)
            self.project_buttons.append(radio)
            radio.show()


    ###  signal handlers
    def on_quit(self, widget, data=None):
        self._toggle_visibility()
        return True

    @threaded
    def on_start(self, data=None):
        self.timesheet.start()
        self._reload()

    @threaded
    def on_stop(self, data=None):
        self.timesheet.stop()
        self._reload()

    def on_projecthours_set(self, data=None):
        radio = [r for r in self.project_buttons[0].get_group() if r.get_active()][0] 
        projectname = radio.get_label()
        project = self.config.get_projects()[projectname]

        self.projecthours_errors = []

        self.days_selection.selected_foreach(self._set_single_projecthours, project)

        if self.projecthours_errors:
            #alert = Gtk.MessageDialog()
            #alert.set_markup("Cannot set project hours for days:\n\n%s" % "\n".join(self.projecthours_errors))
            #alert.show()

            #md = Gtk.MessageDialog(self, Gtk.DialogFlags.DESTROY_WITH_PARENT, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, "Download completed")
            #md.run()
            #md.destroy()
            pass

        self._daylist()

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
            self.window.show()


    def _set_single_projecthours(self, model, path, iter, project=None):
        daydata = [model.get_value(iter, i) for i in range(model.get_n_columns())]

        hours, minutes = daydata[TIME].split(':')

        if self._is_projecthours_day_ready(daydata):
            self.timesheet.set_projecthours(daydata[TIMESTAMP], project, hours, minutes) 
        else:
            self.projecthours_errors.append("%s/%s" %(daydata[NR], daydata[NAME]))

    def _is_projecthours_day_ready(self, daydata):
        return daydata[DESCRIPTION] == "Praca" and \
               daydata[TIMESTAMP] and \
               not daydata[PROJECTHOURS]


    def _quit(self):
        self.window.hide()
        Gtk.main_quit()
        signal.alarm(1)

    @threaded
    def _reload(self):
        self.timesheet.get_hourlist(datetime.now())

        self._hourlist()
        self._month_hours()
        self._daylist()

    # count today hours
    def _today_hours(self):
        (passed, remainig, done) = self.timesheet.get_today_hours()

        # time remaining
        if done:
            remaining_str = '<span fgcolor="%s">+ %s</span>' % ( COLORS['green'], self._timedelta_to_string(passed - timedelta(hours=8)))
        else:
            remaining_str = self._timedelta_to_string(timedelta(hours=8) - passed)

        # time passed
        passed_str = self._timedelta_to_string(passed)

        self.today_passed.set_markup(passed_str)
        self.today_remaining.set_markup(remaining_str)
        data = """Passed:\n<b>%(passed)s</b>\n\nRemaining:\n<b>%(remaining)s</b>""" % {'passed': passed_str, 'remaining': remaining_str}
        if hasattr(self, 'status_icon'):
            self.status_icon.set_tooltip_markup(data)

    @threaded
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
    def _month_hours(self):
        hours = self.timesheet.hours()
        color = COLORS['red'] if hours[0] == '-' else COLORS['green']
        sign = "-" if hours[0] == '-' else "+"
        self.hours.set_markup("<span color='%s' size='large' font_weight='bold'>%s %s</span>" % (color, sign, hours[1:]) ) 

    # formatting for list
    def _hourlist(self):
        hlist = self.timesheet.hourlist
        hlist.reverse()
        self.hours_model.clear()

        for (time, type) in hlist:
            type = type[:2]
            color = COLORS['red'] if type[1] == "K" else COLORS['green']

            self.hours_model.append([str(time), Actions.ext[type], color])


    def _daylist(self):
        daylist = self.timesheet.get_daylist()
        self.days_model.clear()

        for (nr, name, time, description, timestamp, projecthours) in daylist:
            self.days_model.append([nr, 
                                    name, 
                                    time, 
                                    description,
                                    str(timestamp), 
                                    projecthours])


