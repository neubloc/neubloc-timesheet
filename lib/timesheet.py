#!/usr/bin/env python2

import os
import mechanize
import time
from datetime import date, datetime
from datetime import time as time2 

from BeautifulSoup import BeautifulSoup  

from password import *
from actions import *

DEBUG = bool(os.getenv('DEBUG'))


class Timesheet(object):
    
    url = 'http://neubloc.omnis.pl/'

    browser = None
    user = None
    actions = {}

    def __init__(self, user = 'mrim', client = Actions.HOME):
        self.client = client
        self.user = user

        self.actions = Actions.get(client)
        self.login()

    def reload(self):
        self.browser = mechanize.Browser()

    def open(self, page='karta.php'):
        self.browser.open( mechanize.urljoin(self.url, page) )
        self.browser._factory.is_html = True


    # login
    def login(self):
        self.reload()
        self.open()
        self.browser.select_form(nr=0)

        password = Password.get(self.user)

        self.browser["name"] = self.user
        self.browser["pass"] = password 
        self.browser.submit()

    # karta 
    def do(self, action):
        self.login()
        self.open()
        self.browser.select_form(nr=0)

        if DEBUG:
            print("fake submit | action: %s (%s)" % (action, self.actions[action]))
            return

        self.browser.submit(name="action_val", label=self.actions[action])

    def start(self):
        self.do("start")

    def stop(self):
        self.do("stop")

    def hours(self):
        self.login()
        page = self.browser.response().get_data()
        soup = BeautifulSoup(page)
        return soup.find('span', id='tdh_up_plus').text

    # lista 
    def list(self, date = datetime.now()):
        self.login()

        timestamp = time.mktime(date.timetuple())
        self.open("action_popup.php?date=%s" % int(timestamp))
        page = self.browser.response().get_data()

        soup = BeautifulSoup(page)
        rows = soup.find('table', id='userlist').tbody.findAll('tr')

        entries = []

        for row in rows:
            soup = BeautifulSoup(str(row))
            columns = soup.findAll('td', id=None)
            
            if len(columns) > 2:
                entry_time = time2( *time.strptime(columns[1].text,"%H:%M:%S")[3:6] )
                entry_action = columns[2].text
                entries.append((entry_time, entry_action))
                
        return entries


if __name__ == '__main__':
    kp = Timesheet()
    print(kp.list())

