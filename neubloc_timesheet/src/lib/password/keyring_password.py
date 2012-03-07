
# FIXME: glib warning
import keyring
import subprocess

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
        Password.set(user, password.replace("\n", ''))
        
