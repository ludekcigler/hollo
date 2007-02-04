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

#Custom tags for Log

from django import template
from django.utils.dates import MONTHS

from hollo.log import models

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
        choices.append({'value': type.abbr, 'selected': selected, 'name': type.abbr})

    return {'choices': choices}


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

