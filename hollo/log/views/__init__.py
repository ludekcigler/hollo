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

from hollo.log import models

__all__ = ['user', 'workout', 'competition', 'settings']

@decorator.decorator
def login_required(view, *args, **kwargs):
    if kwargs.has_key('request'):
        request = kwargs['request']
    else:
        request = args[0]

    person = models.Person.objects.get(user=request.user)
    if request.user.is_authenticated() and person:
        return view(*args, **kwargs)
    else:
        return index(request)

@decorator.decorator
def athlete_view_allowed(view, *args, **kwargs):
    # The request object
    if kwargs.has_key('request'): request = kwargs['request']
    else: request = args[0]

    # The athlete id, if any
    if kwargs.has_key('athlete_id'): athlete_id = kwargs['athlete_id']
    else: athlete_id = args[1]

    # Check if the user is either a coach or a person authorized to view the athlete logs
    person = models.Person.objects.get(user=request.user)
    athlete = models.Athlete.objects.get(person__user__username=athlete_id)

    if (athlete in person.allowed_athletes()):
        return view(*args, **kwargs)
    else:
        raise "Not allowed to view the athlete"

@decorator.decorator
def athlete_edit_allowed(view, *args, **kwargs):
    # The request object
    if kwargs.has_key('request'): request = kwargs['request']
    else: request = args[0]

    # The athlete id, if any
    if kwargs.has_key('athlete_id'): athlete_id = kwargs['athlete_id']
    else: athlete_id = args[1]

    athlete = models.Athlete.objects.get(person__user__username=athlete_id)

    if athlete.allowed_edit_by(request.user):
        return view(*args, **kwargs)
    else:
        raise "Now allowed to edit athlete"
    

def index(request):
    if request.user.is_authenticated():
        person = models.Person.objects.get(user=request.user)
        if models.Athlete.objects.filter(person__user=request.user).count() > 0:
            athlete_id = request.user.username
        else:
            allowed_athletes = person.allowed_athletes()
            if len(allowed_athletes) > 0:
                athlete_id = allowed_athletes[0].person.user.username
            else:
                #TODO: show error page
                athlete_id = None
        return http.HttpResponseRedirect('/workout/%s/' % (athlete_id, ))
    else:
        return http.HttpResponseRedirect('/login/')

@login_required
def change_athlete(request, view_type):
    """
    Change athlete which is displayed
    """
    person = models.Person.objects.get(user=request.user)
    old_athlete = request.GET.has_key('old') and request.GET['old'] or None
    ctx = RequestContext(request, {'person': person, 'oldAthlete': old_athlete,\
            'viewType': view_type})
    tpl = loader.get_template('log/change_athlete.html')
    return http.HttpResponse(tpl.render(ctx))


def error(request, error_code):
    """
    Displays page with error corresponding to particular error code
    """
    error_code = int(error_code)
    return http.HttpResponse("Error %d" % error_code)
