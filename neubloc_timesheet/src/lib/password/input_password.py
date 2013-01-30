import subprocess

class Password(object):

    @staticmethod
    def get(user):
        password = subprocess.check_output([
            'zenity', '--entry',
            '--title', 'Karta Pracy password',
            '--text',  'Enter your password for Timesheet (%s):' % user,
            '--entry-text', 'password',
            '--hide-text'
        ])
        return password

