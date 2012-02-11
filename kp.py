#!/usr/bin/env python2

import mechanize
import time
import subprocess 

import keyring
from BeautifulSoup import BeautifulSoup  


class Actions(object):
    HOME = 1
    NEUBLOC = 2

    @staticmethod
    def get(client):
        if client == Actions.HOME:
            return { 'start': 'Start dom', 
                     'stop': 'Koniec dom' }       

        elif client == Actions.NEUBLOC:
            return { 'start': 'Start Neubloc', 
                     'stop': 'Koniec Neubloc' } 
        else:
            raise "Client error"

class Password(object):
    service = 'kartapracy'

    @staticmethod
    def get(user):
        while(True):
            try:
                password = keyring.get_password(Password.service, user)
                if password:
                    return password 
                else:
                    raise "no password in keyring"
            except:
                Password.read_and_set(user)

    @staticmethod
    def set(user, password):
        return keyring.set_password(Password.service, user, password)

    @staticmethod
    def read_and_set(user):
        password = subprocess.check_output([
            'zenity', '--entry', 
            '--title', 'Karta Pracy password', 
            '--text',  'Enter your password for Timesheet (%s):' % user, 
            '--entry-text', 'password', 
            '--hide-text'
        ])
        Password.set(user, password)



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
        self.browser.submit(name="action_val", label=self.actions(action))

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
    def list(self, timestamp = time.time()):
        self.login()
        self.open("action_popup.php?date=%s" % int(timestamp))
        page = self.browser.response().get_data()

        soup = BeautifulSoup(page)
        rows = soup.find('table', id='userlist').tbody.findAll('tr')

        entries = []

        for row in rows:
            soup = BeautifulSoup(str(row))
            columns = soup.findAll('td', id=None)
            
            if len(columns) > 2:
                entry = (columns[1].text, columns[2].text)
                entries.append(entry)
                
        return entries


if __name__ == '__main__':
    kp = Timesheet()
    print kp.list()

