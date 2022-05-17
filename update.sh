#!/bin/bash

git clone git@github.com:G0RIAN/USWS-HA-Addon.git
cp ./USWS-HA-Addon/usws.py /config/appdaemon/apps/
rm -r USWS-HA-Addon/