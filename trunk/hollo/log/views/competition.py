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

from hollo.log.views import login_required, athlete_view_allowed, athlete_edit_allowed, get_auth_request_message
from hollo.log import models
from hollo.log import common
from hollo.log import forms

@login_required
@athlete_view_allowed
def index(request, athlete_id):
    today = datetime.date.today()
    return http.HttpResponseRedirect(reverse('log.views.competition.monthly_view',
                                        kwargs={'athlete_id': athlete_id,
                                                'year': today.year,
                                                'month': today.month}))

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

    change_view_data = {'view_type': 'monthly',
                        'year': year, 'month': month}
    change_view_form = forms.CompetitionChangeViewForm(change_view_data, auto_id="competition_change_view_%s")

    t = loader.get_template('log/competition_monthly.html')
    c = RequestContext(request, {'first_day': datetime.date(year, month, 1),\
                                 'competitions': competitions, 'viewType': 'monthly',
                                 'athlete': athlete,
                                 'athlete_edit_allowed': athlete.allowed_edit_by(request.user),
                                 'auth_request_message': get_auth_request_message(request.user.person),
                                 'change_view_form': change_view_form
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

    change_view_data = {'view_type': 'yearly',
                        'year': year, 'month': 1}
    change_view_form = forms.CompetitionChangeViewForm(change_view_data, auto_id="competition_change_view_%s")

    t = loader.get_template('log/competition_yearly.html')
    c = RequestContext(request, {'first_day': datetime.date(year, 1, 1), 'months': months, 'viewType': 'yearly',\
                'athlete': athlete, \
                'athlete_edit_allowed': athlete.allowed_edit_by(request.user), \
                'auth_request_message': get_auth_request_message(request.user.person), \
                'change_view_form': change_view_form
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

    competition_form = forms.CompetitionForm(request.POST, auto_id='competition_%s')
    competition_form.fields["event"].choices = [(e.name, e.name) for e in models.TrackEvent.objects.all()]
    submit_button = common.get_submit_button(request.POST)

    if not submit_button:
        continue_url = request.META.get('HTTP_REFERER', reverse('log.views.workout.index', 
                                                                kwargs={'athlete_id': athlete.person.user.username}))
        competition_form.data = competition_data
    else:
        submit_button = submit_button.lower()
        continue_url = request.GET['continue']
        
        if submit_button == 'ok':
            if save_func(request, athlete, competition_form):
                return http.HttpResponseRedirect(continue_url)
            else:
                context['form_errors'] = True
        else:
            if continue_url:
                return http.HttpResponseRedirect(continue_url)
            else:
                return http.HttpResponseRedirect(reverse('log.views.workout.index', kwargs={'athlete_id': athlete_id}))

    context['continue'] = continue_url
    context['competition_form'] = competition_form
    
    t = loader.get_template('log/competition_form.html')
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
    return http.HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('log.views.index')))


@login_required
@athlete_view_allowed
def change_view(request, athlete_id):
    """
    Change the workout period which is displayed
    """
    form = forms.CompetitionChangeViewForm(request.POST, auto_id="competition_change_view_%s")
    if not form.is_valid():
        return http.HttpResponseRedirect(reverse('log.views.competition.index',
                                                 kwargs={'athlete_id': athlete_id}))
    if (form.cleaned_data['view_type'] == 'monthly'):
        return http.HttpResponseRedirect(reverse('log.views.competition.monthly_view',
                                            kwargs={'athlete_id': athlete_id,
                                                    'year': form.cleaned_data["year"],
                                                    'month': form.cleaned_data["month"]}))
    else:
        month, year = int(request.POST['month']), int(request.POST['year'])
        return http.HttpResponseRedirect(reverse('log.views.competition.yearly_view',
                                            kwargs={'athlete_id': athlete_id,
                                                    'year': form.cleaned_data["year"]}))


def interval_summary(athlete, min_date=None, max_date=None):
    """
    Compute personal bests for all track events the athlete has participated
    in given interval <min_date, max_date>
    """
    track_events = models.TrackEvent.objects.filter(competition__athlete=athlete, has_additional_info=False)
    other_competitions = models.Competition.objects.filter(athlete=athlete, event__has_additional_info=True)

    if min_date:
        track_events = track_events.filter(competition__day__gte=min_date)
        other_competitions = other_competitions.filter(competition__day__gte=min_date)
    if max_date:
        track_events = track_events.filter(competition__day__lte=max_date)
        other_competitions = other_competitions.filter(competition__day__lte=max_date)

    track_events = track_events.distinct()

    summary = {}
    summary["track_events"] = []
    for e in track_events:
        summary_item = {}
        summary_item["event"] = e
        summary_item["best_result"] = athlete.best_result(e, min_date, max_date)
        competitions = models.Competition.objects.filter(event=e, athlete=athlete)
        if min_date:
            competitions = competitions.filter(day__gte=min_date)
        if max_date:
            competitions = competitions.filter(day__lte=max_date)

        summary_item["competitions"] = competitions
        summary["track_events"].append(summary_item)

    summary["other_competitions"] = other_competitions

    return summary
        

