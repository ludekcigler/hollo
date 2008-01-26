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
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404

from athletelog.views import login_required, athlete_view_allowed, athlete_edit_allowed, get_auth_request_message
from athletelog import models
from athletelog import common
from athletelog import forms

@login_required
@athlete_view_allowed
def monthly_view(request, athlete_id, year, month):
    year, month = int(year), int(month)
    first_day = datetime.date(year, month, 1)
    last_day = datetime.date(year, month, calendar.monthrange(year, month)[1])

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

    context = {'previous_month': previous_month, 'previous_year': previous_year,
               'next_month': next_month, 'next_year': next_year}

    return interval_view(request, athlete_id, "monthly", first_day, last_day, context)

@login_required
@athlete_view_allowed
def yearly_view(request, athlete_id, year):
    year = int(year)
    first_day = datetime.date(year, 1, 1)
    last_day = datetime.date(year, 12, calendar.monthrange(year, 12)[1])

    context = {'previous_year': year - 1, 'next_year': year + 1}

    return interval_view(request, athlete_id, "yearly", first_day, last_day, context)

@login_required
@athlete_view_allowed
def index(request, athlete_id):
    return interval_view(request, athlete_id, "all")

def interval_view(request, athlete_id, view_type, first_day = None, last_day = None, initial_context = None):
    athlete = get_object_or_404(models.Athlete, person__user__username=athlete_id)

    competitions = models.Competition.objects.filter(athlete=athlete).order_by('day')
    
    if first_day:
        competitions = competitions.filter(day__gte=first_day)
    if last_day:
        competitions = competitions.filter(day__lte=last_day)

    if first_day:
        year, month = first_day.year, first_day.month
    else:
        year, month = time.localtime()[0:2]

    change_view_data = {'view_type': view_type,
                        'year': year, 
                        'month': month}
    change_view_form = forms.CompetitionChangeViewForm(change_view_data, auto_id="change_view_%s")

    context = {'first_day': first_day,
               'competitions': competitions, 
               'athlete': athlete,
               'athlete_edit_allowed': athlete.allowed_edit_by(request.user),
               'auth_request_message': get_auth_request_message(request.user.person),
               'change_view_form': change_view_form,
               'competition_view_type': view_type,
               'competition_summary': interval_summary(athlete, first_day, last_day)
              }

    if initial_context:
        initial_context.update(context)
        context = initial_context

    t = loader.get_template('athletelog/competition.html')

    c = RequestContext(request, context)
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
    competition_data = {'day': date, 'event': '50 m', 'place': '', 'result': ''}
    return display_form(request, 'add', athlete, date, competition_data, add_submit)

@login_required
@athlete_edit_allowed
def edit_form(request, athlete_id, year, month, day, competition_id):
    """
    Display edit form for competition
    """
    year, month, day = int(year), int(month), int(day)
    date = datetime.date(year, month, day)
    athlete = models.Athlete.objects.get(person__user__username=athlete_id)

    competition = get_object_or_404(models.Competition, pk=competition_id)
    competition_data = {'id': competition_id, 'day': date, 'event': competition.event.name,
                        'event_info': competition.event_info, 'result': competition.result,
                        'place': competition.place, 'note': competition.note}
    return display_form(request, 'edit', athlete, date, competition_data, edit_submit)


def add_submit(request, athlete, competition_form):
    """
    Add new competition
    """
    if not competition_form.is_valid():
        return False

    try:
        event = models.TrackEvent.objects.get(name=competition_form.cleaned_data['event'])
    except ObjectDoesNotExist:
        return False

    # Check the result against regexp
    if not event.check_result(competition_form.cleaned_data['result']):
        competition_form.errors['result'] = 'The result does not match the pattern'
        return False

    competition = models.Competition(athlete=athlete,
                                     event=event,
                                     day=competition_form.cleaned_data['day'],
                                     event_info=competition_form.cleaned_data['event_info'],
                                     place=competition_form.cleaned_data['place'],
                                     result=competition_form.cleaned_data['result'],
                                     note=competition_form.cleaned_data['note'])
    competition.save()
    return True

def edit_submit(request, athlete, competition_form):
    """
    Edit a competition
    """
    if not competition_form.is_valid() or not competition_form.data['id']:
        return False

    competition_id = competition_form.cleaned_data['id']

    try:
        competition = models.Competition.objects.get(id=competition_id)
    except ObjectDoesNotExist:
        return False

    try:
        competition.event = models.TrackEvent.objects.get(name=competition_form.cleaned_data['event'])
    except ObjectDoesNotExist:
        return False

    competition.place = competition_form.cleaned_data['place']
    competition.result = competition_form.cleaned_data['result']
    competition.note = competition_form.cleaned_data['note']
    competition.save()
    return True

def display_form(request, action, athlete, day, competition_data, save_func):
    context = {}
    context['day'] = day
    context['form_action'] = action
    context['athlete'] = athlete

    submit_button = common.get_submit_button(request.POST)

    if not submit_button:
        continue_url = request.META.get('HTTP_REFERER', reverse('athletelog.views.competition.index', 
                                                                kwargs={'athlete_id': athlete.person.user.username}))
        competition_form = forms.CompetitionForm(initial=competition_data, auto_id='competition_%s')
        competition_form.fields["event"].choices = [(e.name, e.name) for e in models.TrackEvent.objects.all()]
    else:
        submit_button = submit_button.lower()
        continue_url = request.GET['continue']
        competition_form = forms.CompetitionForm(request.POST, auto_id='competition_%s')
        competition_form.fields["event"].choices = [(e.name, e.name) for e in models.TrackEvent.objects.all()]
        
        if submit_button == 'ok':
            if save_func(request, athlete, competition_form):
                return http.HttpResponseRedirect(continue_url)
            else:
                context['form_errors'] = True
        else:
            if continue_url:
                return http.HttpResponseRedirect(continue_url)
            else:
                return http.HttpResponseRedirect(reverse('athletelog.views.competition.index', kwargs={'athlete_id': athlete_id}))

    context['continue'] = continue_url
    context['competition_form'] = competition_form
    
    t = loader.get_template('athletelog/competition_form.html')
    c = RequestContext(request, context)
    return http.HttpResponse(t.render(c))

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
    return http.HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('athletelog.views.index')))


@login_required
@athlete_view_allowed
def change_view(request, athlete_id):
    """
    Change the workout period which is displayed
    """
    form = forms.CompetitionChangeViewForm(request.POST, auto_id="change_view_%s")
    if not form.is_valid():
        return http.HttpResponseRedirect(reverse('athletelog.views.competition.index',
                                                 kwargs={'athlete_id': athlete_id}))
    if (form.cleaned_data['view_type'] == 'monthly'):
        return http.HttpResponseRedirect(reverse('athletelog.views.competition.monthly_view',
                                            kwargs={'athlete_id': athlete_id,
                                                    'year': form.cleaned_data["year"],
                                                    'month': form.cleaned_data["month"]}))
    elif (form.cleaned_data['view_type'] == 'yearly'):
        month, year = int(request.POST['month']), int(request.POST['year'])
        return http.HttpResponseRedirect(reverse('athletelog.views.competition.yearly_view',
                                            kwargs={'athlete_id': athlete_id,
                                                    'year': form.cleaned_data["year"]}))
    else:
        return http.HttpResponseRedirect(reverse('athletelog.views.competition.index',
                                            kwargs={'athlete_id': athlete_id}))


def interval_summary(athlete, first_day=None, last_day=None):
    """
    Compute personal bests for all track events the athlete has participated
    in given interval <first_day, last_day>
    """
    track_events = models.TrackEvent.objects.filter(competition__athlete=athlete, has_additional_info=False)
    competitions_all = models.Competition.objects.filter(athlete=athlete)

    if first_day:
        track_events = track_events.filter(competition__day__gte=first_day)
        competitions_all = competitions_all.filter(day__gte=first_day)
    if last_day:
        track_events = track_events.filter(competition__day__lte=last_day)
        competitions_all = competitions_all.filter(day__lte=last_day)

    competitions_other = competitions_all.filter(event__has_additional_info=True)

    track_events = track_events.distinct()

    summary = {}
    summary["track_events"] = []
    summary["competitions"] = competitions_all
    for e in track_events:
        summary_item = {}
        summary_item["event"] = e
        summary_item["best_result"] = athlete.best_result(e, first_day, last_day)
        competitions = models.Competition.objects.filter(event=e, athlete=athlete)
        if first_day:
            competitions = competitions.filter(day__gte=first_day)
        if last_day:
            competitions = competitions.filter(day__lte=last_day)

        summary_item["competitions"] = competitions
        summary["track_events"].append(summary_item)

    summary["competitions_other"] = competitions_other

    return summary
        

