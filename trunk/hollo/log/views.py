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
        return http.HttpResponseRedirect('/log/week/%04d/%02d/' % (year, week))
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
def log_view_week(request, week, year):
    """
    View workout log for a single week
    """
    week, year = int(week), int(year)
    week = min(datetime.date(year, 12, 28).isocalendar()[1], max(1, week))
    week_data = []

    for day in common.iso_week_gregorian_days(year, week):
        workouts = models.Workout.objects.filter(athlete=request.user.id, \
                                                 date=day)
        try:
            num_workout_items = reduce(lambda x, y: x + y, \
                                   [len(w.workoutitem_set.all()) for w in workouts])
            num_day_rows = reduce(lambda x, y: x + y, \
                                   [max(len(w.workoutitem_set.all()), 1) for w in workouts])
        except TypeError:
            num_workout_items = 0
            num_day_rows = 1

        data = {'day': day, 'workouts': workouts, 'num_workout_items': num_workout_items, \
                'num_day_rows': num_day_rows}
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

    t = loader.get_template('log/workout_weekly.html')
    c = RequestContext(request, {'week': week, 'year': year, 'previous_week': previous_week, \
                                 'previous_year': previous_year, 'next_week': next_week, \
                                 'next_year': next_year, 'week_data': week_data, \
                                 'first_day': first_day, 'viewType': 'weekly'})
    return http.HttpResponse(t.render(c))


@login_required
def log_view_month(request, month, year):
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
                            'workouts': models.Workout.objects.filter(athlete=request.user.id, \
                                                     date=datetime.date(year, month, day)) \
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
    t = loader.get_template('log/workout_monthly.html')
    c = RequestContext(request, data)
    return http.HttpResponse(t.render(c))


@login_required
def workout_info_ajax(request, day, month, year):
    """
    Return HTML fragment with information about given workout for this day
    """
    day = datetime.date(int(year), int(month), int(day))
    workouts = models.Workout.objects.filter(athlete = request.user.id, \
                                          date = day)

    t = loader.get_template('log/ajax/workout_info.html')
    c = RequestContext(request, {'workouts': workouts, 'day': day, 'num_workouts': len(workouts)})
    return http.HttpResponse(t.render(c))


@login_required
def workout_add_form_ajax(request, year, month, day):
    """
    Return HTML fragment with add form for given day
    """
    day = datetime.date(int(year), int(month), int(day))

    t = loader.get_template('log/ajax/workout_form.html')
    c = RequestContext(request, {'phase_items': [None] * 3, 'day': day, 'form_action': 'add'})

    return http.HttpResponse(t.render(c))


@login_required
def workout_add(request):
    """
    Add new workout for given day
    """
    num_workout_items = int(request.POST['num_workout_items'])
    
    day = datetime.date.fromtimestamp(calendar.timegm(time.strptime(request.POST['day'], '%Y-%m-%d')))
    athlete = models.Athlete.objects.get(user=request.user.id)

    workout = models.Workout(athlete=athlete, date=day, weather=request.POST['weather'])
    workout.save()

    _workout_items_save(request, workout, num_workout_items)

    return http.HttpResponseRedirect(request.META.get('HTTP_REFERER', ''))


@login_required
def workout_edit_form(request, day, month, year, workout_id):
    """
    Return HTML fragment with edit form for given workout
    """
    day = datetime.date(int(year), int(month), int(day))
    try:
        workout = models.Workout.objects.get(athlete = request.user.id, \
                                            date = day, id = workout_id)
    except ObjectDoesNotExist:
        return http.HttpResponseNotFound()

    t = loader.get_template('log/ajax/workout_form.html')
    c = RequestContext(request, {'workout': workout, 'phase_items': workout.workoutitem_set.all(), \
                                 'day': day, 'form_action': 'edit'})
    return http.HttpResponse(t.render(c))


@login_required
def workout_edit(request):
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

    return http.HttpResponseRedirect(request.META.get('HTTP_REFERER', ''))


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

    t = loader.get_template('log/competition_monthly.html')
    c = RequestContext(request, {'first_day': datetime.date(year, month, 1)})
    return http.HttpResponse(t.render(c))


@login_required
def competition_view_year(request, year):
    pass
