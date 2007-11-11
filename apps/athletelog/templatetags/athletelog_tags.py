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

#Custom tags for Log

from django import template
from django.utils.dates import MONTHS

from athletelog import models

register = template.Library()


@register.inclusion_tag('tags/option.html', takes_context=True)
def select_year(context, min_year, max_year, selected_year):
    choices = []
    for year in xrange(min_year, max_year + 1):
        selected = (year == selected_year)
        choices.append({'value': year, 'selected': selected, 'name': year})

    return {'choices': choices}


@register.inclusion_tag('tags/option.html', takes_context=True)
def select_month(context, selected_month):
    if context.has_key(selected_month):
        selected_month = context[selected_month]
    choices = []
    for month in xrange(1, 13):
        selected = (month == selected_month)
        choices.append({'value': month, 'selected': selected, 'name': MONTHS[month]})

    return {'choices': choices}


@register.inclusion_tag('tags/option.html', takes_context=True)
def select_workout_type(context, selected_type):
    choices = []
    for type in models.WorkoutType.objects.all():
        selected = (type.abbr == selected_type)
        choices.append({'value': type, 'selected': selected, 'name': type.name})

    return {'choices': choices}


@register.inclusion_tag('tags/option.html', takes_context=True)
def select_competition_event(context, selected_event):
    choices = []
    for event in models.TrackEvent.objects.all():
        selected = (event.name == selected_event)
        choices.append({'value': event.name, 'selected': selected, 'name': event.name})

    return {'choices': choices}


@register.inclusion_tag('tags/option.html', takes_context=True)
def select_athlete_group(context, selected_group):
    choices = [{'value': '', 'selected': False, 'name': '-- Žádná --'}]
    for group in models.AthleteGroup.objects.all():
        selected = (group.id == selected_group)
        choices.append({'value': group.id, 'selected': selected, 'name': group.name})

    return {'choices': choices}


@register.inclusion_tag('tags/settings_submenu.html', takes_context=True)
def settings_submenu(context, active_item):
    return {'active_item': active_item, 
            'person': context.has_key('person') and context['person'] or None,
            'athlete': context.has_key('athlete') and context['athlete'] or None,
            'coach': context.has_key('coach') and context['coach'] or None
           }




@register.simple_tag
def workout_weekly_view_num_day_rows(workouts, competitions):
    if len(workouts) > 0:
        num_workout_rows = reduce(lambda x, y: x + y, 
                [max(w.workout_items.count(), 1) for w in workouts])
    else:
        num_workout_rows = 0

    return str(max(num_workout_rows + competitions.count(), 1))

def resolve_variable_or_string(s, context):
    """
    s may be a variable or a quoted string.

    If s is a quoted string, unquote it and return it.  If s is a variable, 
    resolve it and return it.
    """
    if not s[0] in ("'", '"'):
        return template.resolve_variable(s, context)
    if s[-1] == s[0]:
        s = s[:-1]                  # Strip trailing quote, if any.
    s = s[1:]                       # Strip starting quote.
    return s

