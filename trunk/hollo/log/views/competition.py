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

"""
Competition views
"""

import datetime
import time
import calendar
import itertools
import decorator
import re

from django.core.exceptions import ObjectDoesNotExist
from django import http 
from django.template import loader, Context, RequestContext

from hollo.log.views import login_required, athlete_view_allowed, athlete_edit_allowed, get_auth_request_message
from hollo.log import models
from hollo.log import common

@login_required
@athlete_view_allowed
def index(request, athlete_id):
    today = datetime.date.today()
    return http.HttpResponseRedirect('/competition/%s/month/%04d/%02d/' % (athlete_id, today.year, today.month))

@login_required
@athlete_view_allowed
def monthly_view(request, athlete_id, year, month):
    year, month = int(year), int(month)
    athlete = models.Athlete.objects.get(person__user__username=athlete_id)

    try:
        competitions = models.Competition.objects.filter(athlete=athlete, \
                                day__month=month, day__year=year).order_by('day')
    except ObjectDoesNotExist:
        competitions = []

    t = loader.get_template('log/competition_monthly.html')
    c = RequestContext(request, {'first_day': datetime.date(year, month, 1),\
                                 'competitions': competitions, 'viewType': 'monthly',
                                 'athlete': athlete,
                                 'athlete_edit_allowed': athlete.allowed_edit_by(request.user),
                                 'auth_request_message': get_auth_request_message(request.user.person)
                                 })
    return http.HttpResponse(t.render(c))


@login_required
@athlete_view_allowed
def yearly_view(request, athlete_id, year):
    year = int(year)
    athlete = models.Athlete.objects.get(person__user__username=athlete_id)

    months = []

    for month in xrange(1, 13):
        try:
            competitions = models.Competition.objects.filter(athlete=request.user.id, \
                                day__month=month, day__year=year)
        except ObjectDoesNotExist:
            competitions = []

        month_data = {'first_day': datetime.date(year, month, 1), 'competitions': competitions}
        months.append(month_data)

    t = loader.get_template('log/competition_yearly.html')
    c = RequestContext(request, {'first_day': datetime.date(year, 1, 1), 'months': months, 'viewType': 'yearly',\
                'athlete': athlete, \
                'athlete_edit_allowed': athlete.allowed_edit_by(request.user), \
                'auth_request_message': get_auth_request_message(request.user.person) \
                })
    return http.HttpResponse(t.render(c))


@login_required
@athlete_edit_allowed
def add_form(request, athlete_id, year, month, day):
    """
    Display competition add form for given day
    """
    year, month, day = int(year), int(month), int(day)
    date = datetime.date(year, month, day)
    athlete = models.Athlete.objects.get(person__user__username=athlete_id)

    context = {'competition': {'event': ''}, 
               'day': date, 
               'form_action': 'add/%04d/%02d/%02d' % (year, month, day),
               'form_action_desc': 'nový',
               'athlete': athlete}

    # Look for submit key (we need it to determine which button was actually pressed)
    submit_button = common.get_submit_button(request.POST)

    if submit_button:
        context.update({'continue': request.REQUEST['continue']})
        if (submit_button == 'Ok'):
            return add_submit(request)
        elif (submit_button == 'Cancel'):
            return http.HttpResponseRedirect(request.REQUEST['continue'] or '/')
    else:
        context.update({'continue': request.META.get('HTTP_REFERER', '/')})

    t = loader.get_template('log/competition_form.html')
    c = RequestContext(request, context)

    return http.HttpResponse(t.render(c))


@login_required
@athlete_edit_allowed
def add_submit(request, athlete_id):
    """
    Add new competition
    """
    day = datetime.date.fromtimestamp(calendar.timegm(time.strptime(request.POST['day'], '%Y-%m-%d')))
    athlete = models.Athlete.objects.get(person__user__username=athlete_id)

    #TODO: check the values
    try:
        event = models.TrackEvent.objects.get(name=request.POST['event'])
    except ObjectDoesNotExist:
        return http.HttpResponseNotFound()

    competition = models.Competition(athlete=athlete, event=event, \
                                     day=day, place=request.POST['place'], \
                                     result=request.POST['result'], note=request.POST['note'])
    competition.save()

    redirectUrl = request.META.get('HTTP_REFERER', '/')
    if (request.REQUEST.has_key('continue')):
        redirectUrl = request.REQUEST['continue']

    return http.HttpResponseRedirect(redirectUrl)

@login_required
@athlete_edit_allowed
def edit_form(request, athlete_id, year, month, day, competition_id):
    """
    Displays form to edit a competition
    """
    year, month, day, competition_id = int(year), int(month), int(day), int(competition_id)
    date = datetime.date(year, month, day)
    athlete = models.Athlete.objects.get(person__user__username=athlete_id)

    context = {'competition': {'event': ''}, 
               'day': date, 
               'form_action': 'edit/%04d/%02d/%02d/%d' % (year, month, day, competition_id),
               'form_action_desc': 'Upravit',
               'athlete': athlete}

    # Look for submit key (we need it to determine which button was actually pressed)
    submit_button = common.get_submit_button(request.POST)

    if submit_button:
        context.update({'continue': request.REQUEST['continue']})
        if submit_button == 'Ok':
            return edit_submit(request, athlete_id)
        elif submit_button == 'Cancel':
            return http.HttpResponseRedirect(request.REQUEST['continue'] or '/')
    else:
        try:
            competition = models.Competition.objects.get(id=competition_id)
        except ObjectDoesNotExist:
            return http.HttpResponseNotFound()            
        context.update({'competition': competition,
                        'continue': request.META.get('HTTP_REFERER', '/')})

    t = loader.get_template('log/competition_form.html')
    c = RequestContext(request, context)

    return http.HttpResponse(t.render(c))


@login_required
@athlete_edit_allowed
def edit_submit(request, athlete_id):
    """
    Edit a competition
    """
    competition_id = int(request.POST['id'])

    try:
        competition = models.Competition.objects.get(id=competition_id)
    except ObjectDoesNotExist:
        return http.HttpResponseNotFound()

    #TODO: Check the values for edited competition
    try:
        competition.event = models.TrackEvent.objects.get(name=request.POST['event'])
    except ObjectDoesNotExist:
        return http.HttpResponseNotFound()

    competition.place = request.POST['place']
    competition.result = request.POST['result']
    competition.note = request.POST['note']
    competition.save()

    redirectUrl = request.META.get('HTTP_REFERER', '/')
    if (request.REQUEST.has_key('continue')):
        redirectUrl = request.REQUEST['continue']

    return http.HttpResponseRedirect(redirectUrl)


@login_required
@athlete_edit_allowed
def remove_competition(request, athlete_id, competition_id):
    """
    Remove a competition
    """
    competition_id = int(competition_id)

    try:
        competition = models.Competition.objects.get(id=competition_id)
    except ObjectDoesNotExist:
        return http.HttpResponseNotFound()
    
    competition.delete()
    return http.HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required
@athlete_view_allowed
def change_view(request, athlete_id):
    """
    Change the workout period which is displayed
    """
    if (request.POST['viewType'] == 'monthly'):
        week, year = int(request.POST['month']), int(request.POST['year'])
        return http.HttpResponseRedirect('/competition/%s/month/%04d/%02d/' % (athlete_id, year, month))
    else:
        month, year = int(request.POST['month']), int(request.POST['year'])
        return http.HttpResponseRedirect('/competition/%s/year/%04d/' % (athlete_id, year))
