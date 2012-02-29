#!/bin/bash

echo 
echo "*** Building egg file"

rm -rf build/ dist/ 
python2 setup.py bdist_egg

echo 
echo "*** Deploy to pypi.rimek.org"
scp dist/* storage:/nfs/web/pypi
