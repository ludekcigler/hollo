#!/bin/bash

export PYTHONPATH=$HOME/dev/python-local:.:$HOME/dev/websites/hollo
export DJANGO_SETTINGS_MODULE=hollo_settings
django-admin.py $@
