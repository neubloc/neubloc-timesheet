#!/usr/bin/env python

import os
from setuptools import setup, find_packages


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()

NAME = 'neubloc-timesheet'
VERSION = read('VERSION').replace("\n",'')

setup(
    name = NAME,
    version = VERSION,
    description = 'Control neubloc timesheet from gtk3 app',
    author = 'Linden Lab',
    author_email = 'mrim@neubloc.net',
    packages = find_packages(),
    package_data = {'neubloc_timesheet.src.static': ['*']},
    include_package_data = True,
    long_description = read('README'),
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
        #'PyGObject',
        #'gconf',
        #'pdb',
        #'sphinx'
        'keyring',
    ],
    zip_safe = False,
    entry_points = {
        ## self run egg file
        #'setuptools.installation': [
        #    'eggsecutable = timesheet.run',
        #]
        'console_scripts': [
           # modify script_name with the name you want use from shell
           # $ script_name [params]
           'neubloc_timesheet = neubloc_timesheet.src.timesheet:run',
        ],
    }
)
