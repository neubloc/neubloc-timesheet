
import sys
import gtk
import time
from datetime import date, datetime, timedelta
from datetime import time as time2 

from timesheet import *
        
class TimesheetUI(object):

    def on_window_destroy(self, widget, data=None):
        gtk.main_quit()
     
    def __init__(self):
    
        builder = gtk.Builder()
        builder.add_from_file("gui.glade") 
        
        self.window = builder.get_object("window")
        builder.connect_signals(self)       

        self.hourlist = builder.get_object("hourlist")
        self.hours = builder.get_object("hours")
        self.today_hours = builder.get_object("today")

        self.toggle_home = builder.get_object("client_home")
        self.toggle_neubloc = builder.get_object("client_neubloc")

        builder.get_object("start_action").connect("activate", self.start)
        builder.get_object("stop_action").connect("activate", self.stop)
        builder.get_object("toggle_client_home_action").connect("activate", self.toggle_client)
        builder.get_object("toggle_client_neubloc_action").connect("activate", self.toggle_client)

        self.timesheet = Timesheet()       
        if self.timesheet.client == Actions.HOME:
            self.toggle_home.set_active(True)
        else:
            self.toggle_neubloc.set_active(True)

        self.reload()

    def reload(self):
        hlist  = self.timesheet.list(datetime.now() - timedelta(days=2))

        #count
        count = timedelta(0)
        for h1,h2 in zip(hlist[::2],hlist[1::2]):
            t1 = h1[0]
            minute = -1 if t1.second >= 30 else 0
            t1 = (datetime.combine(date.today(), t1) - timedelta(minutes=minute, seconds=t1.second))

            t2 = h2[0]
            minute = -1 if t2.second >= 30 else 0
            t2 = (datetime.combine(date.today(), t2) - timedelta(minutes=minute, seconds=t2.second))

            count += (t1 - t2)
        self.today_hours.set_text("Today hours:\n%s" % count)

        self.hours.set_text("Month hours:\n%s" % self.timesheet.hours() ) 


        # formatting for list
        hlist.reverse()
        hlist = ["%s / %s\n" % (h[0],h[1]) for h in hlist]
        hlist = "\n".join(h1+h2 for h1,h2 in zip(hlist[::2], hlist[1::2]))

        self.hourlist.set_text(hlist) 

    def start(self, action):
        self.timesheet.start()
        self.reload()

    def stop(self, action):
        self.timesheet.stop()
        self.reload()

    def toggle_client(self, action):
        if(action.get_name() == 'toggle_client_home_action'):
            v  = self.toggle_home.get_active()
            self.toggle_neubloc.set_active( (v+1)%2 )

            self.timesheet.client = Actions.HOME
            self.timesheet.actions = Actions.get(Actions.HOME)

        if(action.get_name() == 'toggle_client_neubloc_action'):
            v  = self.toggle_neubloc.get_active()
            self.toggle_home.set_active( (v+1)%2 )

            self.timesheet.client = Actions.NEUBLOC
            self.timesheet.actions = Actions.get(Actions.NEUBLOC)


if __name__ == "__main__":
    app = TimesheetUI()
    app.window.show()
    gtk.main()



