#!/bin/bash

export PYTHONPATH=$HOME/dev/python-local:.
export DJANGO_SETTINGS_MODULE=hollo_settings
django-admin.py $@
