#!/usr/bin/env python

import os
from setuptools import setup, find_packages
#from DistUtilsExtra.command import build_icons


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()

NAME = 'neubloc-timesheet'
VERSION = read('VERSION').replace("\n",'')
DESCRIPTION = read('README.rst')

setup(
    name = NAME,
    version = VERSION,
    description = 'Control neubloc timesheet from gtk3 app',
    author = 'Linden Lab',
    author_email = 'mrim@neubloc.net',
    packages = find_packages(),
    package_data = {'neubloc_timesheet.src.static': ['*']},
    include_package_data = True,
    long_description = DESCRIPTION,
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
    keywords = 'networking internet neubloc',
    license = 'BSD',
    install_requires = [
        'setuptools',
        'mechanize',
        'BeautifulSoup',
        'keyring',
        'setproctitle',
    ],
    zip_safe = False,
    entry_points = {
        'console_scripts': [
           'neubloc_timesheet = neubloc_timesheet.src.main:run',
           'neubloc_timesheet_install_icons = neubloc_timesheet.src.main:install_icons',
        ],
    },
)
