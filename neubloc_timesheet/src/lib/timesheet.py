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
        self._login()

    def _reload(self):
        self.browser = mechanize.Browser()

    def _open(self, page='karta.php'):
        self.browser.open( mechanize.urljoin(self.url, page) )
        self.browser._factory.is_html = True

    def _login(self):
        self._reload()
        self._open()
        self.browser.select_form(nr=0)

        password = Password.get(self.user)

        self.browser["name"] = self.user
        self.browser["pass"] = password 
        return self.browser.submit()

    def _do(self, action):
        self._login()
        self._open()
        self.browser.select_form(nr=0)

        if DEBUG:
            print("fake submit | action: %s (%s)" % (action, self.actions[action]))
            return

        self.browser.submit(name="action_val", label=self.actions[action])

    ### public 
    def start(self):
        self._do("start")

    def stop(self):
        self._do("stop")

    def hours(self):
        self._login()
        page = self.browser.response().get_data()
        soup = BeautifulSoup(page)
        return soup.find('span', id='tdh_up_plus').text

    def hourlist(self, date = datetime.now()):
        self._login()

        timestamp = time.mktime(date.timetuple())
        self._open("action_popup.php?date=%s" % int(timestamp))
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

    def daylist(self, date = datetime.now()):
        page = self._login()

        #timestamp = time.mktime(date.timetuple())
        #self._open("action_popup.php?date=%s" % int(timestamp))
        #page = self.browser.response().get_data()

        soup = BeautifulSoup(page)
        rows = soup.find('table', id='userlist').tbody.findAll('tr')[2:-5]

        entries = []

        for row in rows:
            soup = BeautifulSoup(str(row))
            columns = soup.findAll('td', id=None)
            
            if len(columns) > 2:
                entry_nr = int(columns[0].b.text)
                entry_name = columns[1].text
                entry_description = columns[4].span.text
                entry_time = columns[6].span.text

                entries.append((entry_nr, entry_name, entry_time, entry_description, 0))
                
        return entries


