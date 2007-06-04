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
Views for the Log application
"""

import datetime
import time
import calendar
import itertools
import decorator
import re

from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django import http 
from django.template import loader, Context, RequestContext
from django.utils import simplejson
from django.contrib import auth
from django.shortcuts import render_to_response

from hollo.log import models
from hollo.log import common

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


def athlete_login(request):
    t = loader.get_template('log/login.html')
    c = Context()
    return http.HttpResponse(t.render(c))


def athlete_auth(request):
    username = request.POST['username']
    password = request.POST['password']
    
    user = auth.authenticate(username=username, password=password)
    if user is not None and user.is_active:
        auth.login(request, user)
        return http.HttpResponseRedirect('/log/')
    else:
        return render_to_response('log/login.html', {'message': u"Soráč, ale zadal's špatně heslo.."})


def athlete_logout(request):
    auth.logout(request)
    return index(request)


@login_required
def workout_view_week(request, week, year, detail_year = None, detail_month = None, detail_day = None):
    """
    View workout log for a single week
    """
    week, year = int(week), int(year)
    week = min(datetime.date(year, 12, 28).isocalendar()[1], max(1, week))
    week_data = []

    for day in common.iso_week_gregorian_days(year, week):
        workouts = models.Workout.objects.filter(athlete=request.user.id, \
                                                 day=day)
        competitions = models.Competition.objects.filter(athlete=request.user.id,
                                    day=day)
        data = {'day': day, 'workouts': workouts, 
                'competitions': competitions
               }
        week_data.append(data)

    if week <= 1:
        previous_week = datetime.date(year - 1, 12, 28).isocalendar()[1]
        previous_year = year - 1
    else:
        previous_week = week - 1
        previous_year = year

    if week >= datetime.date(year, 12, 28).isocalendar()[1]:
        next_week = 1
        next_year = year + 1
    else:
        next_week = week + 1
        next_year = year

    first_day = common.iso_week_day_to_gregorian(year, week, 1)
    if first_day.year < year:
        first_day = datetime.date(year, 1, 1)

    context = {'week': week, 'year': year, 'previous_week': previous_week, \
               'previous_year': previous_year, 'next_week': next_week, \
               'next_year': next_year, 'week_data': week_data, \
               'first_day': first_day, 'viewType': 'weekly'}

    if (detail_year and detail_month and detail_day):
        detail_year, detail_month, detail_day = int(detail_year), int(detail_month), int(detail_day)
        t = loader.get_template('log/workout_weekly_detail.html')
        context.update(workout_day_info(request.user.id, detail_year, detail_month, detail_day))
    else:
        t = loader.get_template('log/workout_weekly.html')

    c = RequestContext(request, context)
    return http.HttpResponse(t.render(c))


@login_required
def workout_view_month(request, month, year, detail_day = None):
    """
    View workout log for a single month
    """
    year, month = int(year), int(month)
    month_data = []
    for week_row, week_number in itertools.izip(calendar.monthcalendar(year, month), \
                                                common.week_numbers_in_month(year, month)):
        week_data = {'week': week_number, 'days': []}
        for day in week_row:
            if day:
                day_data = {'day': datetime.date(year, month, day),
                            'workouts': models.Workout.objects.filter(athlete=request.user.id, 
                                                     day=datetime.date(year, month, day)), 
                            'competitions': models.Competition.objects.filter(athlete=request.user.id, 
                                                     day=datetime.date(year, month, day))
                           }
                week_data['days'].append(day_data)
            else:
                week_data['days'].append(None)

        month_data.append(week_data)

    if month == 1:
        previous_year = year - 1
        previous_month = 12
    else:
        previous_year = year
        previous_month = month - 1
    if month == 12:
        next_year = year + 1
        next_month = 1
    else:
        next_year = year
        next_month = month + 1

    data = {'month_data': month_data, 'previous_month': previous_month, 'previous_year': previous_year, \
            'next_month': next_month, 'next_year': next_year, \
            'first_day': datetime.date(year, month, 1), 'viewType': 'monthly'}

    if detail_day:
        data.update(workout_day_info(request.user.id, year, month, int(detail_day)))
        t = loader.get_template('log/workout_monthly_detail.html')
    else:
        t = loader.get_template('log/workout_monthly.html')

    c = RequestContext(request, data)
    return http.HttpResponse(t.render(c))


@login_required
def workout_change_view(request):
    """
    Change the workout period which is displayed
    """
    if (request.POST['viewType'] == 'weekly'):
        week, year = int(request.POST['week']), int(request.POST['year'])
        return http.HttpResponseRedirect('/log/workout/week/%04d/%02d/' % (year, week))
    else:
        month, year = int(request.POST['month']), int(request.POST['year'])
        return http.HttpResponseRedirect('/log/workout/month/%04d/%02d/' % (year, month))


def workout_day_info(athlete, year, month, day):
    """
    Return context dictionary with information about workouts for a given day
    """
    day = datetime.date(int(year), int(month), int(day))
    workouts = models.Workout.objects.filter(athlete=athlete, day=day)
    competitions = models.Competition.objects.filter(athlete=athlete, day=day)

    return {'workouts': workouts, 'day': day, 'num_workouts': len(workouts), 'competitions': competitions}


@login_required
def workout_add_form(request, year, month, day):
    """
    Return HTML add form for given day
    """
    year, month, day = int(year), int(month), int(day)
    date = datetime.date(year, month, day)

    context = {
               'day': date, 
               'form_action': 'add/%04d/%02d/%02d' % (year, month, day),
               'form_action_desc': 'Nový'}

    # Look for submit key (we need it to determine which button was actually pressed)
    submitButton = None
    for key in request.POST:
        m = re.match('^submit([^\.]*).*$', key)
        if m:
            submitButton = m.group(1)

    if not submitButton:
        # Default, the submit key was not pressed before
        context.update({'phase_items': [None] * 3,
                        'continue': request.META.get('HTTP_REFERER', '')
                       })
    else:
        context.update({'continue': request.REQUEST['continue']})

        if (submitButton == 'Ok'):
            return workout_add_submit(request)
        elif (submitButton == 'Cancel'):
            if request.REQUEST['continue']:
                return http.HttpResponseRedirect(request.REQUEST['continue'])
            else:
                return http.HttpResponseRedirect('/log/')
        else:
            context.update(workout_form_update(request, submitButton))

    t = loader.get_template('log/workout_form.html')
    c = RequestContext(request, context)


    return http.HttpResponse(t.render(c))


def workout_form_update(request, submitButton, workout_id = None):
    """
    Updates the workout form after intermediate submits
    """

    # Add new line to the form, maintaining all the form fields the user has entered
    weather = request.POST['weather']
    num_workout_items = int(request.POST['num_workout_items'])
    phase_items = []
    for sequence in xrange(0, num_workout_items):
        type = models.WorkoutType.objects.get(abbr=request.POST['workout_type_%d' % sequence])
        desc = request.POST['workout_desc_%d' % sequence]
        km = request.POST['workout_km_%d' % sequence]
        phase_items.append({'type': type, 'desc': desc, 'km': km})

    if (submitButton == 'AddWorkoutItem'):
        phase_items.append(None)
    else:
        removedItem = int(re.match('^.*_(\d+)$', submitButton).group(1))
        phase_items = phase_items[0:removedItem] + phase_items[removedItem+1:]

    return {'workout': {'id': workout_id, 'weather': weather}, 'phase_items': phase_items}

@login_required
def workout_add_submit(request):
    """
    Add new workout for given day
    """
    num_workout_items = int(request.POST['num_workout_items'])
    
    day = datetime.date.fromtimestamp(calendar.timegm(time.strptime(request.POST['day'], '%Y-%m-%d')))
    athlete = models.Athlete.objects.get(user=request.user.id)

    workout = models.Workout(athlete=athlete, day=day, weather=request.POST['weather'])
    workout.save()

    _workout_items_save(request, workout, num_workout_items)

    redirectUrl = request.META.get('HTTP_REFERER', '')
    if (request.REQUEST.has_key('continue')):
        redirectUrl = request.REQUEST['continue']

    return http.HttpResponseRedirect(redirectUrl)


@login_required
def workout_edit_form(request, day, month, year, workout_id):
    """
    Return HTML fragment with edit form for given workout
    """
    year, month, day = int(year), int(month), int(day)
    workout_id = int(workout_id)
    date = datetime.date(year, month, day)

    # Look for submit key (we need it to determine which button was actually pressed)
    submitButton = None
    for key in request.POST:
        m = re.match('^submit([^\.]*).*$', key)
        if m:
            submitButton = m.group(1)

    context = {
               'day': date, 
               'form_action': 'edit/%04d/%02d/%02d/%d' % (year, month, day, workout_id),
               'form_action_desc': 'Upravit'}

    if not submitButton:
        # Default, the submit key was not pressed before
        try:
            workout = models.Workout.objects.get(id = workout_id)
        except ObjectDoesNotExist:
            return http.HttpResponseNotFound()

        context.update({'workout': workout, 
                        'phase_items': workout.workoutitem_set.all(),
                        'continue': request.META.get('HTTP_REFERER', '/log/')})
    else:
        context.update({'continue': request.REQUEST['continue']})

        if (submitButton == 'Ok'):
            return workout_edit_submit(request)
        elif (submitButton == 'Cancel'):
            if request.REQUEST['continue']:
                return http.HttpResponseRedirect(request.REQUEST['continue'])
            else:
                return http.HttpResponseRedirect('/log/')
        else:
            context.update(workout_form_update(request, submitButton, workout_id))

    t = loader.get_template('log/workout_form.html')
    c = RequestContext(request, context)
    return http.HttpResponse(t.render(c))


@login_required
def workout_edit_submit(request):
    """
    Edit given workout
    """
    workout_id = int(request.POST['id'])
    num_workout_items = int(request.POST['num_workout_items'])

    try:
        workout = models.Workout.objects.get(id=workout_id)
    except ObjectDoesNotExist:
        return http.HttpResponseNotFound()

    workout.weather = request.POST['weather']
    workout.save()

    workout.workoutitem_set.all().delete()
    _workout_items_save(request, workout, num_workout_items)

    redirectUrl = request.META.get('HTTP_REFERER', '/log/')
    if (request.REQUEST.has_key('continue')):
        redirectUrl = request.REQUEST['continue']

    return http.HttpResponseRedirect(redirectUrl)


def _workout_items_save(request, workout, num_workout_items):
    for sequence in xrange(0, num_workout_items):
        workout_type = models.WorkoutType.objects.get(abbr=request.POST['workout_type_%d' % sequence])
        workout_desc = request.POST['workout_desc_%d' % sequence]
        workout_km = request.POST['workout_km_%d' % sequence]

        workoutitem = models.WorkoutItem(workout=workout, sequence=sequence, type=workout_type, \
                                         desc=workout_desc, km=workout_km)
        workoutitem.save()

    return True

@login_required
def workout_remove(request, workout_id):
    """
    Remove specified workout from the DB
    """
    workout_id = int(workout_id)

    try:
        workout = models.Workout.objects.get(id = workout_id)
    except ObjectDoesNotExist:
        return http.HttpResponseNotFound()
    
    workout.delete()
    return http.HttpResponseRedirect(request.META.get('HTTP_REFERER', ''))


@login_required
def competition_view_month(request, year, month):
    year, month = int(year), int(month)

    try:
        competitions = models.Competition.objects.filter(athlete=request.user.id, \
                                day__month=month, day__year=year).order_by('day')
    except ObjectDoesNotExist:
        competitions = []

    t = loader.get_template('log/competition_monthly.html')
    c = RequestContext(request, {'first_day': datetime.date(year, month, 1),\
                                 'competitions': competitions, 'viewType': 'monthly'})
    return http.HttpResponse(t.render(c))


@login_required
def competition_view_year(request, year):
    year = int(year)

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
    c = RequestContext(request, {'first_day': datetime.date(year, 1, 1), 'months': months, 'viewType': 'yearly'})
    return http.HttpResponse(t.render(c))


@login_required
def competition_add_form(request, year, month, day):
    """
    Display competition add form for given day
    """
    year, month, day = int(year), int(month), int(day)
    date = datetime.date(year, month, day)

    context = {'competition': {'event': ''}, 
               'day': date, 
               'form_action': 'add/%04d/%02d/%02d' % (year, month, day),
               'form_action_desc': 'nový'}

    # Look for submit key (we need it to determine which button was actually pressed)
    submitButton = None
    for key in request.POST:
        m = re.match('^submit([^\.]*).*$', key)
        if m:
            submitButton = m.group(1)

    if submitButton:
        context.update({'continue': request.REQUEST['continue']})
        if (submitButton == 'Ok'):
            return competition_add_submit(request)
        elif (submitButton == 'Cancel'):
            return http.HttpResponseRedirect(request.REQUEST['continue'] or '/log/')
    else:
        context.update({'continue': request.META.get('HTTP_REFERER', '/log/')})

    t = loader.get_template('log/competition_form.html')
    c = RequestContext(request, context)

    return http.HttpResponse(t.render(c))


@login_required
def competition_add_submit(request):
    """
    Add new competition
    """
    day = datetime.date.fromtimestamp(calendar.timegm(time.strptime(request.POST['day'], '%Y-%m-%d')))
    athlete = models.Athlete.objects.get(user=request.user.id)

    #TODO: check the values
    try:
        event = models.TrackEvent.objects.get(name=request.POST['event'])
    except ObjectDoesNotExist:
        return http.HttpResponseNotFound()

    competition = models.Competition(athlete=athlete, event=event, \
                                     day=day, place=request.POST['place'], \
                                     result=request.POST['result'], note=request.POST['note'])
    competition.save()

    redirectUrl = request.META.get('HTTP_REFERER', '/log/')
    if (request.REQUEST.has_key('continue')):
        redirectUrl = request.REQUEST['continue']

    return http.HttpResponseRedirect(redirectUrl)

@login_required
def competition_edit_form(request, year, month, day, competition_id):
    """
    Displays form to edit a competition
    """
    year, month, day, competition_id = int(year), int(month), int(day), int(competition_id)
    date = datetime.date(year, month, day)

    context = {'competition': {'event': ''}, 
               'day': date, 
               'form_action': 'edit/%04d/%02d/%02d/%d' % (year, month, day, competition_id),
               'form_action_desc': 'Upravit'}

    # Look for submit key (we need it to determine which button was actually pressed)
    submitButton = None
    for key in request.POST:
        m = re.match('^submit([^\.]*).*$', key)
        if m:
            submitButton = m.group(1)

    if submitButton:
        context.update({'continue': request.REQUEST['continue']})
        if submitButton == 'Ok':
            return competition_edit_submit(request)
        elif submitButton == 'Cancel':
            return http.HttpResponseRedirect(request.REQUEST['continue'] or '/log/')
    else:
        try:
            competition = models.Competition.objects.get(id=competition_id)
        except ObjectDoesNotExist:
            return http.HttpResponseNotFound()            
        context.update({'competition': competition,
                        'continue': request.META.get('HTTP_REFERER', '/log/')})

    t = loader.get_template('log/competition_form.html')
    c = RequestContext(request, context)

    return http.HttpResponse(t.render(c))


@login_required
def competition_edit_submit(request):
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

    redirectUrl = request.META.get('HTTP_REFERER', '/log/')
    if (request.REQUEST.has_key('continue')):
        redirectUrl = request.REQUEST['continue']

    return http.HttpResponseRedirect(redirectUrl)


@login_required
def competition_remove(request, competition_id):
    """
    Remove a competition
    """
    competition_id = int(competition_id)

    try:
        competition = models.Competition.objects.get(id=competition_id)
    except ObjectDoesNotExist:
        return http.HttpResponseNotFound()
    
    competition.delete()
    return http.HttpResponseRedirect(request.META.get('HTTP_REFERER', ''))

@login_required
def competition_change_view(request):
    """
    Change the competition period which is displayed
    """
    if (request.POST['viewType'] == 'monthly'):
        month, year = int(request.POST['month']), int(request.POST['year'])
        return http.HttpResponseRedirect('/log/competition/month/%04d/%02d/' % (year, month))
    else:
        year = int(request.POST['year'])
        return http.HttpResponseRedirect('/log/competition/year/%04d/' % year)
