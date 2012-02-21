
import gconf

from actions import *

class Config(object):

    keybase = '/apps/neubloc-timesheet/'

    def __init__(self):
        try:
            self.client = gconf.client_get_default()
        except:
            print "client error"

    def _get(self, key, default=None):
        val = self.client.get_string(self._expand(key))
        if not val:
            self._set(key, default)
            val = self.client.get_string(self._expand(key))
        return val

    def _set(self, key, val):
        self.client.set_string(self._expand(key), str(val))

    def _expand(self, keyname):
        return self.keybase + keyname.lstrip('/')


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
        return False if self._get('minimized', False) == '0' else True

    def set_minimized(self, val):
        return self._set('minimized', int(val))


    def get_user(self):
        return self._get('user', 'mrim')

    def set_user(self, val):
        return self._set('user', val)

    def get_projects(self):
        default = {'PJPJ': (44, 27), 
                   'BZBZ': (50, 66)};
        #projects['NBSA'] = {'company_id': 24, 'project_id': 79};

        return self._get('projects', default)



