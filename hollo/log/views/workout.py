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
Views specific for the workout section
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

from hollo.log.views import login_required
from hollo.log import models
from hollo.log import common

@login_required
def weekly_view(request, week, year, detail_year = None, detail_month = None, detail_day = None):
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
        context.update(day_info(request.user.id, detail_year, detail_month, detail_day))
    else:
        t = loader.get_template('log/workout_weekly.html')

    c = RequestContext(request, context)
    return http.HttpResponse(t.render(c))


@login_required
def monthly_view(request, month, year, detail_day = None):
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
        data.update(day_info(request.user.id, year, month, int(detail_day)))
        t = loader.get_template('log/workout_monthly_detail.html')
    else:
        t = loader.get_template('log/workout_monthly.html')

    c = RequestContext(request, data)
    return http.HttpResponse(t.render(c))


@login_required
def change_view(request):
    """
    Change the workout period which is displayed
    """
    if (request.POST['viewType'] == 'weekly'):
        week, year = int(request.POST['week']), int(request.POST['year'])
        return http.HttpResponseRedirect('/log/workout/week/%04d/%02d/' % (year, week))
    else:
        month, year = int(request.POST['month']), int(request.POST['year'])
        return http.HttpResponseRedirect('/log/workout/month/%04d/%02d/' % (year, month))


def day_info(athlete, year, month, day):
    """
    Return context dictionary with information about workouts for a given day
    """
    day = datetime.date(int(year), int(month), int(day))
    workouts = models.Workout.objects.filter(athlete=athlete, day=day)
    competitions = models.Competition.objects.filter(athlete=athlete, day=day)

    return {'workouts': workouts, 'day': day, 'num_workouts': len(workouts), 'competitions': competitions}


@login_required
def add_form(request, year, month, day):
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
    submit_button = None
    for key in request.POST:
        m = re.match('^submit([^\.]*).*$', key)
        if m:
            submit_button = m.group(1)

    if not submit_button:
        # Default, the submit key was not pressed before
        context.update({'phase_items': [None] * 3,
                        'continue': request.META.get('HTTP_REFERER', '')
                       })
    else:
        context.update({'continue': request.REQUEST['continue']})

        if (submit_button == 'Ok'):
            return add_submit(request)
        elif (submit_button == 'Cancel'):
            if request.REQUEST['continue']:
                return http.HttpResponseRedirect(request.REQUEST['continue'])
            else:
                return http.HttpResponseRedirect('/log/')
        else:
            context.update(form_context_update(request, submit_button))

    t = loader.get_template('log/workout_form.html')
    c = RequestContext(request, context)


    return http.HttpResponse(t.render(c))


def form_context_update(request, submit_button, workout_id = None):
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

    if (submit_button == 'AddWorkoutItem'):
        phase_items.append(None)
    else:
        removedItem = int(re.match('^.*_(\d+)$', submit_button).group(1))
        phase_items = phase_items[0:removedItem] + phase_items[removedItem+1:]

    return {'workout': {'id': workout_id, 'weather': weather}, 'phase_items': phase_items}

@login_required
def add_submit(request):
    """
    Add new workout for given day
    """
    num_workout_items = int(request.POST['num_workout_items'])
    
    day = datetime.date.fromtimestamp(calendar.timegm(time.strptime(request.POST['day'], '%Y-%m-%d')))
    athlete = models.Athlete.objects.get(person=request.user.id)

    workout = models.Workout(athlete=athlete, day=day, weather=request.POST['weather'])
    workout.save()

    _workout_items_save(request, workout, num_workout_items)

    redirectUrl = request.META.get('HTTP_REFERER', '')
    if (request.REQUEST.has_key('continue')):
        redirectUrl = request.REQUEST['continue']

    return http.HttpResponseRedirect(redirectUrl)


@login_required
def edit_form(request, day, month, year, workout_id):
    """
    Return HTML fragment with edit form for given workout
    """
    year, month, day = int(year), int(month), int(day)
    workout_id = int(workout_id)
    date = datetime.date(year, month, day)

    # Look for submit key (we need it to determine which button was actually pressed)
    submit_button = None
    for key in request.POST:
        m = re.match('^submit([^\.]*).*$', key)
        if m:
            submit_button = m.group(1)

    context = {
               'day': date, 
               'form_action': 'edit/%04d/%02d/%02d/%d' % (year, month, day, workout_id),
               'form_action_desc': 'Upravit'}

    if not submit_button:
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

        if (submit_button == 'Ok'):
            return edit_submit(request)
        elif (submit_button == 'Cancel'):
            if request.REQUEST['continue']:
                return http.HttpResponseRedirect(request.REQUEST['continue'])
            else:
                return http.HttpResponseRedirect('/log/')
        else:
            context.update(form_context_update(request, submit_button, workout_id))

    t = loader.get_template('log/workout_form.html')
    c = RequestContext(request, context)
    return http.HttpResponse(t.render(c))


@login_required
def edit_submit(request):
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
def remove_workout(request, workout_id):
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

