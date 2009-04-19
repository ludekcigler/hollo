#!/bin/bash

PYTHONPATH=`python -c 'import sys; print ":".join(sys.path);'`
export PYTHONPATH=$HOME/dev/python-local:.:$HOME/dev/websites/hollo:$HOME/dev/django-apps/hollo/trunk/:$PYTHONPATH
export DJANGO_SETTINGS_MODULE=hollo_settings

python manage.py $@
