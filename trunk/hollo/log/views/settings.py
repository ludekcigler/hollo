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

"""
Views for settings adjustments
"""

from django.template import loader, Context, RequestContext
from django.core.exceptions import ObjectDoesNotExist
from django import http 

from hollo.log import views
from hollo.log.views import login_required
from hollo.log import models
from hollo.log import common

@login_required
def index(request):
    """
    Default settings URL, just redirects to the proper default screen
    """
    return http.HttpResponseRedirect('/log/settings/user/')


@login_required
def user(request):
    """
    Display user-specific settings
    """
    person = models.Person.objects.get(user=request.user.id)
    athlete = models.Athlete.objects.filter(person=request.user.id).count() == 1 and \
                models.Athlete.objects.get(person=request.user.id) or None
    coach = models.Coach.objects.filter(person=request.user.id).count() == 1 and \
                models.Coach.objects.get(person=request.user.id) or None

    context = {'person': person, 'athlete': athlete, 'coach': coach}

    tpl = loader.get_template('log/settings_user.html')
    context = RequestContext(request, context)
    return http.HttpResponse(tpl.render(context))


@login_required
def my_athletes(request):
    """
    Display settings for coach groups
    """
    try:
        coach = models.Coach.objects.get(person=request.user.id)
    except ObjectDoesNotExist:
        return http.HttpResponseRedirect('/log/settings/')

    tpl = loader.get_template('log/settings_my_athletes.html')
    context = RequestContext(request, {'coach': coach})
    return http.HttpResponse(tpl.render(context))

@login_required
def friends(request):
    """
    View settings for which people can see your workout logs
    """
    try:
        athlete = models.Athlete.objects.get(person=request.user.id)
    except ObjectDoesNotExist:
        return http.HttpResponseRedirect('/log/settings/')

    tpl = loader.get_template('log/settings_friends.html')
    context = RequestContext(request, {'athlete': athlete})
    return http.HttpResponse(tpl.render(context))


