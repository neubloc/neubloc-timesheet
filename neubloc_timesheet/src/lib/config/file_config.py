import os
import subprocess
from ConfigParser import ConfigParser

from actions import *

class Config(object):

    file_path = '~/.config/neubloc-timesheet.conf'

    def __init__(self):
        self.file_path = os.path.expanduser(self.file_path)
        if not os.path.exists(self.file_path):
            self.write_template()

        try:
            config = ConfigParser()
            config.read(self.file_path)

            self.main_section = config.sections()[0]
            self.config = config
        except:
            print "Config/keyring client error"

    def _get(self, key, default=None, section='main'):
        val = self.config.get(section, key)
        if not val:
            self._set(key, default, section)
            val = self.config.get(key, default, section)
        return val

    def _get_only(self, key, section='main'):
        return self.config.get(section, key)

    def _set(self, key, val, section='main'):
        self.config.set(section, key, str(val))
        with open(self.file_path, 'w') as f:
            self.config.write(f)

    # ---------------------------------------

    def write_template(self):
        data = (
            ('client', 'neubloc'), # neubloc/home
            ('user', 'mrim'),
            ('minimized', '1'),
        )
        projects = (
            ('PJ', '44,27'),
            ('SMP', '50,66'),
            ('PreSales', '24,79'),
            ('BaS', '59,92'),
        )

        c = ConfigParser()
        c.add_section('main')
        for key,value in data:
            c.set('main', key, value)

        c.add_section('projects')
        for key,value in projects:
            c.set('projects', key, value)

        with open(self.file_path, 'w') as f:
            c.write(f)


    # ---------------------------------------

    def get_client(self):
        c = self._get('client', 'home')
        if c == 'home':
            return Actions.HOME
        elif c == 'neubloc':
            return Actions.NEUBLOC

    def set_client(self, val):
        if val == Actions.HOME:
            val = 'home'
        elif val == Actions.NEUBLOC:
            val = 'neubloc'
        self._set('client', val)


    def get_minimized(self):
        return False if self._get('minimized', 0) == '0' else True

    def set_minimized(self, val):
        return self._set('minimized', int(val))


    def get_user(self, default=None):
        if not self._get_only('user'):
            user = self.prompt_for_user()
            self.set_user(user)

        return self._get_only('user')

    def set_user(self, val):
        return self._set('user', val)

    def get_projects(self):
        return dict(self.config.items('projects'))

    def prompt_for_user(self):
        user = subprocess.check_output([
            'zenity', '--entry',
            '--title', 'Timesheet username',
            '--text',  'Enter your login for Timesheet:',
            '--entry-text', 'login'
        ])
        return user.replace("\n", '')



