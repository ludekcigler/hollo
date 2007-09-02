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
from django.core.urlresolvers import reverse

from hollo.log.views import login_required, athlete_view_allowed, \
                            athlete_edit_allowed, get_auth_request_message, \
                            force_no_cache
from hollo.log import models
from hollo.log import common

@login_required
@athlete_view_allowed
def index(request, athlete_id):
    year, week = datetime.date.today().isocalendar()[:2]
    return http.HttpResponseRedirect(reverse('log.views.workout.weekly_view', 
                                     kwargs={'athlete_id': athlete_id,
                                             'year': year,
                                             'week': week}))

@login_required
@athlete_view_allowed
@force_no_cache
def weekly_view(request, athlete_id, week, year, detail_year = None, detail_month = None, detail_day = None):
    """
    View workout log for a single week
    """
    athlete = models.Athlete.objects.get(person__user__username=athlete_id)

    week, year = int(week), int(year)
    week = min(datetime.date(year, 12, 28).isocalendar()[1], max(1, week))
    week_data = []

    for day in common.iso_week_gregorian_days(year, week):
        workouts = models.Workout.objects.filter(athlete=athlete, \
                                                 day=day)
        competitions = models.Competition.objects.filter(athlete=athlete,
                                    day=day)
        data = {'date': day, 'workouts': workouts, 
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
               'first_day': first_day, 'viewType': 'weekly',
               'athlete': athlete,
               'athlete_edit_allowed': athlete.allowed_edit_by(request.user),
               'auth_request_message': get_auth_request_message(request.user.person)}

    if (detail_year and detail_month and detail_day):
        detail_year, detail_month, detail_day = int(detail_year), int(detail_month), int(detail_day)
        t = loader.get_template('log/workout_weekly_detail.html')
        context.update(day_info(athlete, detail_year, detail_month, detail_day))
    else:
        t = loader.get_template('log/workout_weekly.html')

    c = RequestContext(request, context)
    return http.HttpResponse(t.render(c))

def weekly_view_detail(*args, **kwargs):
    return weekly_view(*args, **kwargs)

def weekly_summary(athlete, year, week):
    """
    Returns a summary for a given athlete, year and week.
    This includes:
    - total number of workouts
    - total km
    - average satisfaction
    """



@login_required
@athlete_view_allowed
@force_no_cache
def monthly_view(request, athlete_id, month, year, detail_day = None):
    """
    View workout log for a single month
    """
    athlete = models.Athlete.objects.get(person__user__username=athlete_id)

    year, month = int(year), int(month)
    month_data = []
    for week_row, week_number in itertools.izip(calendar.monthcalendar(year, month), \
                                                common.week_numbers_in_month(year, month)):
        week_data = {'week': week_number, 'days': []}
        for day in week_row:
            if day:
                day_data = {'date': datetime.date(year, month, day),
                            'workouts': models.Workout.objects.filter(athlete=athlete, 
                                                     day=datetime.date(year, month, day)), 
                            'competitions': models.Competition.objects.filter(athlete=athlete, 
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
            'first_day': datetime.date(year, month, 1), 'viewType': 'monthly',
            'athlete': athlete,
            'athlete_edit_allowed': athlete.allowed_edit_by(request.user),
            'auth_request_message': get_auth_request_message(request.user.person)}

    if detail_day:
        data.update(day_info(athlete, year, month, int(detail_day)))
        t = loader.get_template('log/workout_monthly_detail.html')
    else:
        t = loader.get_template('log/workout_monthly.html')

    c = RequestContext(request, data)
    return http.HttpResponse(t.render(c))

def monthly_view_detail(*args, **kwargs):
    return monthly_view(*args, **kwargs)

@login_required
@athlete_view_allowed
def change_view(request, athlete_id):
    """
    Change the workout period which is displayed
    """
    if (request.POST['viewType'] == 'weekly'):
        week, year = int(request.POST['week']), int(request.POST['year'])
        return http.HttpResponseRedirect(reverse('log.views.workout.weekly_view',
                                                 kwargs={'athlete_id': athlete_id,
                                                         'year': year,
                                                         'week': week}))    
    else:
        month, year = int(request.POST['month']), int(request.POST['year'])
        return http.HttpResponseRedirect(reverse('log.views.workout.monthly_view',
                                                 kwargs={'athlete_id': athlete_id,
                                                         'year': year,
                                                         'month': month}))


def day_info(athlete, year, month, day):
    """
    Return context dictionary with information about workouts for a given day
    """
    day = datetime.date(int(year), int(month), int(day))
    workouts = models.Workout.objects.filter(athlete=athlete, day=day)
    competitions = models.Competition.objects.filter(athlete=athlete, day=day)

    return {'workouts': workouts, 'day': day, 'num_workouts': len(workouts), 'competitions': competitions}


@login_required
@athlete_edit_allowed
def add_form(request, athlete_id, year, month, day):
    """
    Return HTML add form for given day
    """
    athlete = models.Athlete.objects.get(person__user__username=athlete_id)

    year, month, day = int(year), int(month), int(day)
    date = datetime.date(year, month, day)

    context = {
               'day': date, 
               'form_action': 'add',
               'athlete': athlete}

    # Look for submit key (we need it to determine which button was actually pressed)
    submit_button = common.get_submit_button(request.POST)

    if not submit_button:
        # Default, the submit key was not pressed before
        context.update({'phase_items': [None] * 3,
                        'continue': request.META.get('HTTP_REFERER', '')
                       })
    else:
        context.update({'continue': request.REQUEST['continue']})

        if (submit_button == 'Ok'):
            return add_submit(request, athlete_id)
        elif (submit_button == 'Cancel'):
            if request.REQUEST['continue']:
                return http.HttpResponseRedirect(request.REQUEST['continue'])
            else:
                return http.HttpResponseRedirect(reverse('log.views.index'))
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
    note = request.POST['note']
    rating_satisfaction = min(models.Workout.MAX_RATING, max(models.Workout.MIN_RATING, int(request.POST['rating_satisfaction'])))
    rating_difficulty = min(models.Workout.MAX_RATING, max(models.Workout.MIN_RATING, int(request.POST['rating_difficulty'])))
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

    return {'workout': \
                {'id': workout_id, \
                'weather': weather, \
                'note': note, \
                'rating_satisfaction': rating_satisfaction, \
                'rating_difficulty': rating_difficulty \
                }, \
            'phase_items': phase_items}

@login_required
@athlete_edit_allowed
def add_submit(request, athlete_id):
    """
    Add new workout for given day
    """
    num_workout_items = int(request.POST['num_workout_items'])
    
    day = datetime.date.fromtimestamp(calendar.timegm(time.strptime(request.POST['day'], '%Y-%m-%d')))
    athlete = models.Athlete.objects.get(person__user__username=athlete_id)

    workout = models.Workout(athlete=athlete,
                             day=day, 
                             weather=request.POST['weather'],
                             note=request.POST['note'],
                             rating_satisfaction = min(models.Workout.MAX_RATING, max(models.Workout.MIN_RATING, int(request.POST['rating_satisfaction']))),
                             rating_difficulty = min(models.Workout.MAX_RATING, max(models.Workout.MIN_RATING, int(request.POST['rating_difficulty']))))

    workout.save()

    _workout_items_save(request, workout, num_workout_items)

    redirectUrl = request.META.get('HTTP_REFERER', reverse('log.views.index'))
    if (request.REQUEST.has_key('continue')):
        redirectUrl = request.REQUEST['continue']

    return http.HttpResponseRedirect(redirectUrl)


@login_required
@athlete_edit_allowed
def edit_form(request, athlete_id, day, month, year, workout_id):
    """
    Return HTML fragment with edit form for given workout
    """
    year, month, day = int(year), int(month), int(day)
    workout_id = int(workout_id)
    date = datetime.date(year, month, day)

    athlete = models.Athlete.objects.get(person__user__username=athlete_id)

    # Look for submit key (we need it to determine which button was actually pressed)
    submit_button = common.get_submit_button(request.POST)

    context = {
               'day': date, 
               'form_action': 'edit',
               'athlete': athlete}

    if not submit_button:
        # Default, the submit key was not pressed before
        try:
            workout = models.Workout.objects.get(id = workout_id)
        except ObjectDoesNotExist:
            return http.HttpResponseNotFound()

        context.update({'workout': workout, 
                        'phase_items': workout.workout_items.all(),
                        'continue': request.META.get('HTTP_REFERER', reverse('log.views.index'))})
    else:
        context.update({'continue': request.REQUEST['continue']})

        if (submit_button == 'Ok'):
            return edit_submit(request, athlete_id)
        elif (submit_button == 'Cancel'):
            if request.REQUEST['continue']:
                return http.HttpResponseRedirect(request.REQUEST['continue'])
            else:
                return http.HttpResponseRedirect(reverse('log.views.index'))
        else:
            context.update(form_context_update(request, submit_button, workout_id))

    t = loader.get_template('log/workout_form.html')
    c = RequestContext(request, context)
    return http.HttpResponse(t.render(c))


@login_required
@athlete_edit_allowed
def edit_submit(request, athlete_id):
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
    workout.note = request.POST['note']
    workout.rating_satisfaction = min(models.Workout.MAX_RATING, max(models.Workout.MIN_RATING, int(request.POST['rating_satisfaction'])))
    workout.rating_difficulty = min(models.Workout.MAX_RATING, max(models.Workout.MIN_RATING, int(request.POST['rating_difficulty'])))
    workout.save()

    workout.workout_items.all().delete()
    _workout_items_save(request, workout, num_workout_items)

    redirectUrl = request.META.get('HTTP_REFERER', reverse('log.views.index'))
    if (request.REQUEST.has_key('continue')):
        redirectUrl = request.REQUEST['continue']

    return http.HttpResponseRedirect(redirectUrl)


def _workout_items_save(request, workout, num_workout_items):
    for sequence in xrange(0, num_workout_items):
        workout_type = models.WorkoutType.objects.get(abbr=request.POST['workout_type_%d' % sequence])
        workout_desc = request.POST['workout_desc_%d' % sequence]
        workout_num_data = request.POST['workout_km_%d' % sequence]

        workoutitem = models.WorkoutItem(workout=workout, sequence=sequence, type=workout_type, \
                                         desc=workout_desc, num_data=workout_num_data)
        workoutitem.save()

    return True

@login_required
@athlete_edit_allowed
def remove_workout(request, athlete_id, workout_id):
    """
    Remove specified workout from the DB
    """
    workout_id = int(workout_id)

    try:
        workout = models.Workout.objects.get(id = workout_id)
    except ObjectDoesNotExist:
        return http.HttpResponseNotFound()
    
    workout.delete()
    return http.HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('log.views.index')))
