
import sys
import gtk
import time

from kp import *
        
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

        self.toggle_home = builder.get_object("client_home")
        self.toggle_neubloc = builder.get_object("client_neubloc")

        builder.get_object("start_action").connect("activate", self.start)
        builder.get_object("stop_action").connect("activate", self.stop)
        builder.get_object("toggle_client_home_action").connect("activate", self.toggle_client)
        builder.get_object("toggle_client_neubloc_action").connect("activate", self.toggle_client)

        self.reload()

    def reload(self):
        self.timesheet = Timesheet()       
        hlist  = self.timesheet.list(time.time() - 24*60*60)
        hlist.reverse()
        hlist = ["%s / %s\n" % (h[0],h[1]) for h in hlist]
        #hlist = "\n".join( h[0] + ' / ' + h[1] for h in hlist )
        #hlist = "\n".join( str(h1) + ' / ' + str(h2) + '\n' for h1,h2 in zip(hlist[::2], hlist[1::2]) )
        hlist = "\n".join(h1+h2 for h1,h2 in zip(hlist[::2], hlist[1::2]))

        self.hourlist.set_text(hlist) 
        self.hours.set_text( self.timesheet.hours() ) 

    def start(self, action):
        print 'self.timesheet.start()'
        self.reload()

    def stop(self, action):
        print 'self.timesheet.stop()'
        self.reload()

    def toggle_client(self, action):
        if(action.get_name() == 'toggle_client_home_action'):
            v  = self.toggle_home.get_active()
            self.toggle_neubloc.set_active( (v+1)%2 )

        if(action.get_name() == 'toggle_client_neubloc_action'):
            v  = self.toggle_neubloc.get_active()
            self.toggle_home.set_active( (v+1)%2 )
        #v = self.toggle_home.get_active()
        #self.toggle_home.set_active( (v+1)%2 ) 


if __name__ == "__main__":
    app = TimesheetUI()
    app.window.show()
    gtk.main()



