#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import mechanize
import time
from datetime import datetime, timedelta
from datetime import time as time2
import re

from threading import Lock

from BeautifulSoup import BeautifulSoup

from password import Password
from actions import Actions

DEBUG = bool(os.getenv('DEBUG'))
NR, NAME, TIME, DESCRIPTION, TIMESTAMP, PROJECTHOURS = range(6)

class Timesheet(object):

    url = 'http://neubloc.omnis.pl/'

    browser = None
    user = None
    actions = {}

    _hourlist = None
    _daylist = None

    _hourlist_lock = Lock()
    _daylist_lock = Lock()

    def __init__(self, user = 'mrim', client = Actions.HOME):
        self.client = client
        self.user = user

        self.actions = Actions.get(client)
        #self._login()

    @property
    def hourlist(self):
        self._hourlist_lock.acquire()
        value = self._hourlist
        self._hourlist_lock.release()
        return value

    @hourlist.setter
    def hourlist(self, value):
        self._hourlist_lock.acquire()
        self._hourlist = value
        self._hourlist_lock.release()

    @property
    def daylist(self):
        self._daylist_lock.acquire()
        value = self._daylist
        self._daylist_lock.release()
        return value

    @daylist.setter
    def daylist(self, value):
        self._daylist_lock.acquire()
        self._daylist = value
        self._daylist_lock.release()

    def _reload(self):
        self.browser = mechanize.Browser()

    def _open(self, page='karta.php'):
        #import pdb; pdb.set_trace()
        self.browser.open( mechanize.urljoin(self.url, page) )
        self.browser._factory.is_html = True

    def _login(self):
        self._reload()
        self._open()
        self._select_form('login_form')

        password = Password.get(self.user)
        # @TODO remove
        password = password.replace("\n", '')
        self.user = self.user.replace("\n", '')

        self.browser["name"] = self.user
        self.browser["pass"] = password
        return self.browser.submit()

    def _do(self, action):
        self._login()
        self._select_form('action_form')

        if DEBUG:
            print("fake submit | action: %s (%s)" % (action, self.actions[action]))
            return

        self.browser.submit(name="action_val", label=self.actions[action])

    def _select_form(self, form_id):
        self.browser._factory.is_html = True
        self.browser.select_form(predicate=lambda f: 'id' in f.attrs and f.attrs['id'] == form_id)

    ### public
    def start(self):
        self._do("start")

    def stop(self):
        self._do("stop")

    def hours(self):
        page = self._login()
        soup = BeautifulSoup(page)
        return soup.find('span', id='tdh_up_plus').text

    def get_hourlist(self, date = datetime.now()):
        if DEBUG:
            entries = [
             (datetime(1,1,1,19, 00, 11).time(), 'OS (Start Dom)'),
             (datetime(1,1,1,16, 46, 11).time(), 'DK (Koniec Dom)'),
             (datetime(1,1,1,8,  34, 58).time(), 'DS (Start Dom)')
            ]
            self.hourlist = entries
            return entries

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

            try:
                if 'strokeout' in row.attrs[0][1]: continue
            except IndexError: pass

            if len(columns) > 2:
                entry_time = time2( *time.strptime(columns[1].text,"%H:%M:%S")[3:6] )
                # round to 30 sec
                try:
                    entry_time = entry_time.replace(minute=entry_time.minute-1, second=0) if entry_time.second >= 30 else entry_time.replace(second=0)
                except ValueError:
                    pass

                entry_action = columns[2].text
                entries.append((entry_time, entry_action))

        self.hourlist = entries
        #FIXME
        print entries[-1]
        return entries

    def get_daylist(self, date = datetime.now()):

        page = self._login()

        soup = BeautifulSoup(page)
        rows = soup.find('table', id='userlist').tbody.findAll('tr')[2:-5]

        entries = []

        for row in rows:
            soup = BeautifulSoup(unicode(row))

            columns = soup.findAll('td', id=None)

            if len(columns) > 2:
                entry_nr = int(columns[0].b.text)
                entry_name = columns[1].text
                entry_description = columns[4].span.text
                entry_time = columns[6].span.text

                timestamp = ''
                try:
                    r = re.compile('.*date\=(\d+)')
                    timestamp = r.findall(columns[0]['onclick'])[0]
                except KeyError: pass

                # registered projecthours
                process_projecthours = lambda c: "%s / %s" % (c.span['title'], c.span.text) if c.span.text else None
                projecthours = filter(None, [process_projecthours(c) for c in columns[12:]])
                projecthours = "\n".join(projecthours)

                entries.append((entry_nr,
                                entry_name,
                                entry_time,
                                entry_description,
                                timestamp,
                                projecthours))

        self.daylist = entries
        return entries

    def set_projecthours(self, timestamp, project, hours, minutes):
        self._login()
        self._open('task_popup.php?date=%s' % timestamp)
        self.browser.select_form(nr=0)

        company_id, project_id = project.split(',')
        self.browser["company_id"] = [str(company_id)]
        self.browser["project_id"] = [str(project_id)]
        self.browser["task_type_id"] = ["1"]
        self.browser["num_hours"] = str(hours)
        self.browser["num_mins"] = str(minutes)
        submit =  self.browser.find_control("user_action")
        submit.disabled = False

        if DEBUG:
            print "(fake) Setting %s:%s on day %s / project: %s" % (hours, minutes, timestamp, project)
            return

        self.browser.submit()

    def get_today_hours(self, date = datetime.now()):
        if not self.hourlist:
            return (timedelta(0), timedelta(0), False)
        hlist = self.hourlist

        delta = timedelta(0)
        nonedate = datetime(1,1,1,0,0,0)
        for h1,h2 in zip(hlist[::2],hlist[1::2]):
            t1 = datetime.combine(nonedate, h1[0])
            t2 = datetime.combine(nonedate, h2[0])
            delta += (t2-t1)

        if len(hlist) % 2 == 1:
            delta += datetime.now() - datetime.combine(datetime.now(), hlist[-1][0])
        passed_delta = delta

        # time remaining
        done = False
        rdelta = timedelta(hours=8) - delta
        if(rdelta < timedelta(hours=0)):
            rdelta = delta - timedelta(hours=8)
            done = True
        remaining_delta = delta

        return (passed_delta, remaining_delta, done)



