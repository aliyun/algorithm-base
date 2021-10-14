#! /usr/bin/env bash
pip3 uninstall -y ab
rm -rf src/ab.egg-info
python3 setup.py sdist
pip3 install dist/ab-2.1.13.tar.gz -v
ls -l /Library/Frameworks/Python.framework/Versions/3.6/lib/python3.6/site-packages/ab/