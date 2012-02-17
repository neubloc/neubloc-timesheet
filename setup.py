#!/usr/bin/env python

from setuptools import setup

setup(
    name='neubloc-timesheet',
    version='0.1',
    description='Control neubloc timesheet from gtk3 app',
    author='Linden Lab',
    author_email='mrim@neubloc.net',
    packages=['neubloc-timesheet'],

    long_description="""\
    eventlet is a coroutines-based network library for python ...
    """,
    classifiers=[
      "License :: OSI Approved :: GNU General Public License (GPL)",
      "Programming Language :: Python",
      "Development Status :: Beta",
      "Intended Audience :: Developers",
      "Topic :: Internet",
    ],
    keywords='networking internet neubloc',
    license='GPL',
    install_requires=[
    'setuptools',
    'mechanize',
    'PyGObject',
    'vimpdb',
    'keyring',
    'gconf',
    'sphinx'
    ],
)
