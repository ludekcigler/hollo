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
from django.shortcuts import get_object_or_404
from django.utils import simplejson

from athletelog.views import login_required, athlete_view_allowed, \
                            athlete_edit_allowed, get_auth_request_message, \
                            force_no_cache
from athletelog import models
from athletelog import common
from athletelog import forms
from athletelog.views import competition

@login_required
@athlete_view_allowed
def index(request, athlete_id):
    year, week = datetime.date.today().isocalendar()[:2]
    return weekly_view(request, athlete_id, year, week)
    return http.HttpResponseRedirect(reverse('athletelog.views.workout.weekly_view', 
                                     kwargs={'athlete_id': athlete_id,
                                             'year': year,
                                             'week': week}))

def _weekly_view_context(request, athlete, year, week):
    """
    Loads context for weekly view
    """
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
    last_day = common.iso_week_day_to_gregorian(year, week, 7)

    context = {'week': week, 'year': year, 'previous_week': previous_week, \
               'previous_year': previous_year, 'next_week': next_week, \
               'next_year': next_year, 'week_data': week_data, \
               'first_day': first_day, 
               'last_day': last_day,
              }
    return context

@login_required
@athlete_view_allowed
@force_no_cache
def weekly_view(request, athlete_id, year, week, detail_year = None, detail_month = None, detail_day = None, template = 'athletelog/workout_weekly.html'):
    """
    View workout log for a single week
    """
    try:
        athlete = models.Athlete.objects.select_related().get(person__user__username=athlete_id)
    except ObjectDoesNotExist:
        return http.HttpResponseNotFound()

    context = _weekly_view_context(request, athlete, year, week)

    change_view_data = {'view_type': 'weekly', 'week': context['week'], 'year': context['year'], 'month': context['first_day'].month}
    change_view_form = forms.WorkoutChangeViewForm(change_view_data, auto_id="change_view_%s")

    context.update({'view_type': 'weekly',
               'athlete': athlete,
               'athlete_edit_allowed': athlete.allowed_edit_by(request.user),
               'auth_request_message': get_auth_request_message(request.user.person),
               'change_view_form': change_view_form})

    if (detail_year and detail_month and detail_day):
        detail_year, detail_month, detail_day = int(detail_year), int(detail_month), int(detail_day)
        t = loader.get_template('athletelog/workout_weekly_detail.html')
        context.update(day_info(athlete, detail_year, detail_month, detail_day))
    else:
        context["workout_summary"] = interval_summary(athlete, context['first_day'], context['last_day'])
        context["competition_summary"] = competition.interval_summary(athlete, context['first_day'], context['last_day'])
        t = loader.get_template(template)


    c = RequestContext(request, context)
    return http.HttpResponse(t.render(c))

def weekly_view_detail(*args, **kwargs):
    return weekly_view(*args, **kwargs)

def interval_summary(athlete, min_date, max_date):
    """
    Returns a summary for a given athlete, min- and max- date.
    This includes:
    - total number of workouts
    - total km
    - average satisfaction
    """
    summary = {}
    summary["workouts"] = models.Workout.objects.filter(athlete=athlete, day__gte=min_date, day__lte=max_date)
    summary["total_km"] = sum([w.total_km for w in summary["workouts"]])
    summary["total_workouts"] = summary["workouts"].count()
    if summary["total_workouts"] > 0:
        summary["satisfaction_avg"] = sum([w.rating_satisfaction for w in summary["workouts"]]) / float(summary["total_workouts"])
        summary["difficulty_avg"] = sum([w.rating_difficulty for w in summary["workouts"]]) / float(summary["total_workouts"])
    else:
        summary["satisfaction_avg"] = None
        summary["difficulty_avg"] = None

    return summary

@login_required
@athlete_view_allowed
@force_no_cache
def monthly_view(request, athlete_id, year, month, detail_day = None, template = 'athletelog/workout_monthly.html'):
    """
    View workout log for a single month
    """
    athlete = models.Athlete.objects.select_related().get(person__user__username=athlete_id)

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

    first_day = datetime.date(year, month, 1)
    last_day = datetime.date(year, month, calendar.monthrange(year, month)[1])

    change_view_data = {'view_type': 'monthly', 'week': common.week_numbers_in_month(year, month).next(),
                        'year': year, 'month': month}
    change_view_form = forms.WorkoutChangeViewForm(change_view_data, auto_id="change_view_%s")

    context = {'month_data': month_data, 'previous_month': previous_month, 'previous_year': previous_year, \
            'next_month': next_month, 'next_year': next_year, \
            'first_day': first_day, 'view_type': 'monthly',
            'year': year, 'month': month,
            'athlete': athlete,
            'athlete_edit_allowed': athlete.allowed_edit_by(request.user),
            'auth_request_message': get_auth_request_message(request.user.person),
            'change_view_form': change_view_form}

    if detail_day:
        context.update(day_info(athlete, year, month, int(detail_day)))
        t = loader.get_template('athletelog/workout_monthly_detail.html')
    else:
        context["workout_summary"] = interval_summary(athlete, first_day, last_day)
        context["competition_summary"] = competition.interval_summary(athlete, first_day, last_day)
        t = loader.get_template(template)

    c = RequestContext(request, context)
    return http.HttpResponse(t.render(c))

def monthly_view_detail(*args, **kwargs):
    return monthly_view(*args, **kwargs)

@login_required
@athlete_view_allowed
def change_view(request, athlete_id):
    """
    Change the workout period which is displayed
    """
    form = forms.WorkoutChangeViewForm(request.POST, auto_id="change_view_%s")
    if not form.is_valid():
        return http.HttpResponseRedirect(reverse('athletelog.views.workout.index', kwargs={'athlete_id': athlete_id}))

    if (form.cleaned_data["view_type"] == 'weekly'):
        return http.HttpResponseRedirect(reverse('athletelog.views.workout.weekly_view',
                                                 kwargs={'athlete_id': athlete_id,
                                                         'year': form.cleaned_data["year"],
                                                         'week': form.cleaned_data["week"]}))    
    else:
        return http.HttpResponseRedirect(reverse('athletelog.views.workout.monthly_view',
                                                 kwargs={'athlete_id': athlete_id,
                                                         'year': form.cleaned_data["year"],
                                                         'month': form.cleaned_data["month"]}))


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
def add_form(request, athlete_id, year, month, day, template = 'athletelog/workout_form.html'):
    athlete = get_object_or_404(models.Athlete, person__user__username=athlete_id)
    year, month, day = int(year), int(month), int(day)
    date = datetime.date(year, month, day)
    workout_data = {'num_workout_items': 3, 'rating_satisfaction': 3, 'rating_difficulty': 3, 'day': date}

    return display_form(request, 'add', athlete, date, workout_data, 3, {}, add_submit, template)

@login_required
@athlete_edit_allowed
def edit_form(request, athlete_id, year, month, day, workout_id, template = 'athletelog/workout_form.html'):
    athlete = get_object_or_404(models.Athlete, person__user__username=athlete_id)
    year, month, day = int(year), int(month), int(day)
    date = datetime.date(year, month, day)
    num_workout_items = models.WorkoutItem.objects.filter(workout__pk=workout_id).count()

    workout = models.Workout.objects.get(pk=workout_id)
    workout_data = {'day': workout.day, 'id': workout_id, 'num_workout_items': num_workout_items,
                    'weather': workout.weather, 'rating_satisfaction': workout.rating_satisfaction,
                    'rating_difficulty': workout.rating_difficulty, 'note': workout.note}

    workout_items_data = {}
    for workout_item in workout.workout_items.all():
        seq = workout_item.sequence
        workout_items_data['workout_item_%d_type' % seq] = workout_item.type.abbr
        workout_items_data['workout_item_%d_desc' % seq] = workout_item.desc
        workout_items_data['workout_item_%d_num_data' % seq] = workout_item.num_data
    
    return display_form(request, 'edit', athlete, date, workout_data,
                        num_workout_items, workout_items_data, edit_submit, template)
    

def display_form(request, action, athlete, date, workout_data, num_workout_items, workout_items_data, save_func, template):
    """
    Return HTML add/edit form for given workout
    @param action               Either "add" or "edit"
    @param athlete              ID of an athlete
    @param workout_data         Dictionary with data about workout
    @param num_workout_items    Number of workout items
    @param workout_items_data   List of dictionaries with data of workout items
    @param save_func            Function to save data to
    """
    context = {}
    context['day'] = date, 
    context['form_action'] = action
    context['athlete'] = athlete

    workout_item_forms = []

    # Look for submit key (we need it to determine which button was actually pressed)
    submit_button = common.get_submit_button(request.POST)

    if not submit_button:
        # Default, the submit key was not pressed before
        continue_url = request.META.get('HTTP_REFERER', reverse('athletelog.views.workout.index', 
                                                                kwargs={'athlete_id': athlete.person.user.username}))
        workout_form = forms.WorkoutForm(initial=workout_data, auto_id='workout_%s')
        workout_item_forms = _create_workout_item_forms(num_workout_items, workout_items_data)
    else:
        submit_button = submit_button.lower()
        continue_url = request.GET['continue']

        if submit_button == 'cancel':
            if continue_url:
                return http.HttpResponseRedirect(continue_url)
            else:
                return http.HttpResponseRedirect(reverse('athletelog.views.workout.index', kwargs={'athlete_id': athlete_id}))

        num_workout_items = int(request.POST['num_workout_items'])

        if submit_button == 'ok':
            workout_form = forms.WorkoutForm(request.POST.copy(), auto_id='workout_%s')
            workout_item_forms = _create_workout_item_forms(num_workout_items, data=request.POST.copy())
            form_valid, errors = save_func(request, athlete, workout_form, workout_item_forms)
            if form_valid:
                return http.HttpResponseRedirect(continue_url)
            else:
                # There were errors in workout form -- redisplay the form
                context['form_errors'] = True
        else:
            workout_item_forms = _create_workout_item_forms(num_workout_items, initial=request.POST.copy())
            workout_form = forms.WorkoutForm(initial=request.POST.copy(), auto_id='workout_%s')
            if submit_button == 'add_workout_item':
                workout_item_forms.append(forms.WorkoutItemForm(auto_id=(('workout_item_%d_' % num_workout_items) + '%s')))
                num_workout_items += 1
                workout_form.initial['num_workout_items'] = num_workout_items
    
            else:
                # Remove the workout item
                removed_item = int(re.match('^.*_(\d+)$', submit_button).group(1))
                del workout_item_forms[removed_item]
                num_workout_items -= 1
                workout_form.initial['num_workout_items'] = num_workout_items

                # Update IDs of workout item forms
                for f, i in zip(workout_item_forms, range(0, len(workout_item_forms))):
                    f.auto_id = (('workout_item_%d_' % i) + '%s')

    context['continue'] = continue_url
    context['workout_form'] = workout_form
    context['workout_item_forms'] = workout_item_forms

    t = loader.get_template(template)
    c = RequestContext(request, context)
    return http.HttpResponse(t.render(c))


def _create_workout_item_forms(num_workout_items, data={}, initial={}):
    """
    Creates workout item forms
    """
    posted_data = initial
    if data:
        posted_data = data
        
    result_forms = []
    workout_type_choices = [(t.abbr, t.abbr) for t in models.WorkoutType.objects.all()]
    for i in xrange(0, num_workout_items):

        item_data = {}
        item_data_post_fields = ["workout_item_%d_type", "workout_item_%d_desc", "workout_item_%d_num_data"]
        item_data_fields = ["type", "desc", "num_data"]
        for post_field, field in zip(item_data_post_fields, item_data_fields):
            if posted_data.has_key(post_field % i):
                item_data[field] = posted_data[post_field % i]

        if data:
            workout_item_form = forms.WorkoutItemForm(item_data, auto_id=(('workout_item_%d_' % i) + '%s'))
        else:
            workout_item_form = forms.WorkoutItemForm(initial=item_data, auto_id=(('workout_item_%d_' % i) + '%s'))

        workout_item_form.fields["type"].choices = workout_type_choices
        result_forms.append(workout_item_form)

    return result_forms

def add_submit(request, athlete, workout_form, workout_item_forms):
    """
    Add new workout for given day
    """
    errors = {'workout': [], 'workout_items': []}
    forms_valid = True
    # Check validity in the forms
    if not workout_form.is_valid():
        errors['workout'] = workout_form.errors
        forms_valid = forms_valid and False
    for form in workout_item_forms:
        workout_item_errors = []
        if not form.is_valid():
            workout_item_errors = form.errors
            forms_valid = forms_valid and False
        errors['workout_items'].append(workout_item_errors)

    if not forms_valid:
        return False, errors

    num_workout_items = workout_form.cleaned_data['num_workout_items']
    day = workout_form.cleaned_data['day']

    workout = models.Workout(athlete=athlete,
                             day=day, 
                             weather=workout_form.cleaned_data['weather'],
                             note=workout_form.cleaned_data['note'],
                             rating_satisfaction=workout_form.cleaned_data['rating_satisfaction'],
                             rating_difficulty=workout_form.cleaned_data['rating_difficulty'])
    workout.save()

    _workout_items_save(request, workout, workout_item_forms)

    return True, errors


def edit_submit(request, athlete, workout_form, workout_item_forms):
    """
    Submit "edit workout" form
    """
    errors = {'workout': [], 'workout_items': []}
    forms_valid = True
    # Check validity in the forms
    if not workout_form.is_valid():
        errors['workout'] = workout_form.errors
        forms_valid = forms_valid and False
    for form in workout_item_forms:
        workout_item_errors = []
        if not form.is_valid():
            workout_item_errors = form.errors
            forms_valid = forms_valid and False
        errors['workout_items'].append(workout_item_errors)

    if not forms_valid:
        return False, errors

    num_workout_items = workout_form.cleaned_data['num_workout_items']
    day = workout_form.cleaned_data['day']

    workout = models.Workout.objects.get(pk=workout_form.cleaned_data['id'])

    workout.weather = workout_form.cleaned_data['weather']
    workout.note = workout_form.cleaned_data['note']
    workout.rating_satisfaction = workout_form.cleaned_data['rating_satisfaction']
    workout.rating_difficulty = workout_form.cleaned_data['rating_difficulty']
    workout.save()

    workout.workout_items.all().delete()
    _workout_items_save(request, workout, workout_item_forms)

    return True, errors

def _workout_items_save(request, workout, workout_items_forms):
    for form, sequence in zip(workout_items_forms, range(0, len(workout_items_forms))):
        workout_type = models.WorkoutType.objects.get(abbr=form.cleaned_data['type'])
        workout_item = models.WorkoutItem(workout=workout, 
                                         sequence=sequence, 
                                         type=workout_type,
                                         desc=form.cleaned_data['desc'],
                                         num_data=form.cleaned_data['num_data'])
        workout_item.save()

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
    return http.HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('athletelog.views.index')))

@login_required
@athlete_view_allowed
def api_weekly_view(request, athlete_id, week, year):
    try:
        athlete = models.Athlete.objects.select_related().get(person__user__username=athlete_id)
    except ObjectDoesNotExist:
        return http.HttpResponseNotFound()

    context = _weekly_view_context(request, athlete, week, year)

    return http.HttpResponse(common.jsonify(context))

def api_monthly_view(request, athlete_id, month, year):
    return http.HttpResponseNotFound()

@login_required
@athlete_view_allowed
def daily_summary_snippet(request, athlete_id, year, month, day):
    try:
        athlete = models.Athlete.objects.get(person__user__username=athlete_id)
    except ObjectDoesNotExist:
        return http.HttpResponseNotFound()

    year, month, day = int(year), int(month), int(day)

    context = day_info(athlete, year, month, day)
    context["athlete"] = athlete
    context["athlete_edit_allowed"] = athlete.allowed_edit_by(request.user)

    t = loader.get_template('athletelog/include/workout_info.html')
    c = RequestContext(request, context)
    return http.HttpResponse(t.render(c))

@login_required
@athlete_view_allowed
def weekly_summary_snippet(request, athlete_id, year, week):
    year, week = int(year), int(week)
    first_day = common.iso_week_day_to_gregorian(year, week, 1)
    last_day = common.iso_week_day_to_gregorian(year, week, 7)

    return interval_summary_snippet(request, athlete_id, first_day, last_day, template='athletelog/include/workout_weekly_summary.html')

@login_required
@athlete_view_allowed
def monthly_summary_snippet(request, athlete_id, year, month):
    year, month = int(year), int(month)
    first_day = datetime.date(year, month, 1)
    last_day = datetime.date(year, month, calendar.monthrange(year, month)[1])

    return interval_summary_snippet(request, athlete_id, first_day, last_day, template='athletelog/include/workout_monthly_summary.html')

def interval_summary_snippet(request, athlete_id, first_day, last_day, template='athletelog/include/workout_summary.html'):
    try:
        athlete = models.Athlete.objects.get(person__user__username=athlete_id)
    except ObjectDoesNotExist:
        return http.HttpResponseNotFound()

    context = {}
    context["workout_summary"] = interval_summary(athlete, first_day, last_day)
    context["competition_summary"] = competition.interval_summary(athlete, first_day, last_day)
    context["athlete_edit_allowed"] = athlete.allowed_edit_by(request.user)

    t = loader.get_template(template)
    c = RequestContext(request, context)
    return http.HttpResponse(t.render(c))

@login_required
@athlete_view_allowed
def weekly_view_snippet(request, athlete_id, year, week):
    return weekly_view(request, athlete_id, year, week, template='athletelog/include/workout_weekly.html')

@login_required
@athlete_view_allowed
def monthly_view_snippet(request, athlete_id, year, month):
    return monthly_view(request, athlete_id, year, month, template='athletelog/include/workout_monthly.html')

@login_required
@athlete_edit_allowed
def add_form_snippet(request, athlete_id, year, month, day):
    return add_form(request, athlete_id, year, month, day, template = 'athletelog/include/workout_form.html');

@login_required
@athlete_edit_allowed
def edit_form_snippet(request, athlete_id, year, month, day, workout_id):
    return edit_form(request, athlete_id, year, month, day, workout_id, template = 'athletelog/include/workout_form.html');

@login_required
@athlete_edit_allowed
def api_add_workout(request, athlete_id):
    return _api_save_workout(request, athlete_id, add_submit)

@login_required
@athlete_edit_allowed
def api_edit_workout(request, athlete_id):
    return _api_save_workout(request, athlete_id, edit_submit)

def _api_save_workout(request, athlete_id, save_func):
    try:
        athlete = models.Athlete.objects.get(person__user__username=athlete_id)
    except ObjectDoesNotExist:
        return http.HttpResponseNotFound()
    if request.POST.has_key('num_workout_items'):
        num_workout_items = int(request.POST['num_workout_items'])
    else:
        num_workout_items = 0

    workout_form = forms.WorkoutForm(request.POST.copy(), auto_id='workout_%s')
    workout_item_forms = _create_workout_item_forms(num_workout_items, data=request.POST.copy())

    form_valid, errors = save_func(request, athlete, workout_form, workout_item_forms)

    errors_cleaned = ['workout_%s' % field for field in errors['workout']]
    for i, item_errors in zip(xrange(0, len(errors['workout_items'])), errors['workout_items']):
        errors_cleaned.extend(['workout_item_%d_%s' % (i, elem) for elem in item_errors])

    response = {'response': form_valid and 'ok' or 'failed', 'errors': errors_cleaned}
    return http.HttpResponse(simplejson.dumps(response))
