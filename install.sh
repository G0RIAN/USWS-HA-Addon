#!/bin/bash

git clone git@github.com:G0RIAN/USWS-HA-Addon.git
cp ./USWS-HA-Addon/usws.py /config/appdaemon/apps/
cat ./USWS-HA-Addon/apps.yaml >> /config/appdaemon/apps/apps.yaml
rm -r USWS-HA-Addon/