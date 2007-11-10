# -*- coding: utf-8 -*-
##
## Copyright (C) 2007 Luděk Cigler <lcigler@gmail.com>
##
## This file is part of Hollo.
##
## Hollo is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 3 of the License, or
## (at your option) any later version.
##
## Hollo is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program. If not, see <http://www.gnu.org/licenses/>.
##

import datetime
import decorator
import time

from django.core.exceptions import ObjectDoesNotExist
from django.core import urlresolvers
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


@decorator.decorator
def force_no_cache(view, *args, **kwargs):
    """
    Wraps the response object and sets its HTTP headers
    so that browsers should not cache contents of the page
    """
    response = view(*args, **kwargs)
    response['Last-modified'] = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())
    return response
    

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
        return http.HttpResponseRedirect(urlresolvers.reverse('log.views.workout.index', kwargs = {'athlete_id': athlete_id}))
    else:
        return http.HttpResponseRedirect(urlresolvers.reverse('log.views.user.login'))

@login_required
def change_athlete(request, view_type):
    """
    Change athlete which is displayed
    """
    person = models.Person.objects.get(user=request.user)
    old_athlete = request.GET.has_key('old') and request.GET['old'] or None
    ctx = RequestContext(request, {'person': person, 'old_athlete': old_athlete,\
            'view_type': view_type})
    tpl = loader.get_template('log/change_athlete.html')
    return http.HttpResponse(tpl.render(ctx))


def error(request, error_code):
    """
    Displays page with error corresponding to particular error code
    """
    error_code = int(error_code)
    return http.HttpResponse("Error %d" % error_code)

# Helper functions for views

def get_auth_request_message(person):
    try:
        athlete = models.Athlete.objects.get(person=person)
    except ObjectDoesNotExist:
        return None

    auth_request_count = athlete.auth_request_to.count()
    if auth_request_count <= 0:
        return None
    elif auth_request_count == 1:
        return "1 požadavek na autorizaci"
    elif auth_request_count >= 2 and auth_request_count < 5:
        return "%d požadavky na autorizaci" % auth_request_count
    else:
        return "%d požadavků na autorizaci" % auth_request_count

# Generate list of information about track events
def js_event_info(request):
    track_events = models.TrackEvent.objects.all()
    t = loader.get_template('log/js_event_info.js')
    context = RequestContext(request, {'events': track_events})
    return http.HttpResponse(t.render(context))

# Generate list of information about workout types
def js_workout_type_info(request):
    workout_types = models.WorkoutType.objects.all()
    t = loader.get_template('log/js_workout_type_info.js')
    context = RequestContext(request, {'workout_types': workout_types})
    return http.HttpResponse(t.render(context))
