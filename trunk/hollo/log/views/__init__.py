# -*- coding: utf-8 -*-
##
## Copyright (C) 2007 Luděk Cigler <lcigler@gmail.com>
##
## This file is part of Hollo.
##
## Hollo is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## Tsine is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Hollo; if not, write to the Free Software
## Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
##

import datetime
import decorator

from django.core.exceptions import ObjectDoesNotExist
from django import http 
from django.template import loader, Context, RequestContext

__all__ = ['user', 'workout', 'competition', 'settings']

@decorator.decorator
def login_required(view, *args, **kwargs):
    if kwargs.has_key('request'):
        request = kwargs['request']
    else:
        request = args[0]

    if request.user.is_authenticated():
        return view(*args, **kwargs)
    else:
        return index(request)


def index(request):
    if request.user.is_authenticated():
        # Compute current week and send the user to that week
        year, week = datetime.date.today().isocalendar()[:2]
        return http.HttpResponseRedirect('/log/workout/week/%04d/%02d/' % (year, week))
    else:
        return http.HttpResponseRedirect('/log/login/')
