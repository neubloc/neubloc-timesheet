#!/bin/bash

echo 
echo "*** Building egg file"

rm -rf build/ dist/ 
python2 setup.py bdist_egg

echo 
echo "*** Deploy to pypi.rimek.org"
scp dist/* storage:/nfs/web/pypi

echo
echo "*** Installing from pypi.rimek.org"
easy_install-2.7 http://pypi.m.rimek.org/neubloc_timesheet-0.1-py2.7.egg
