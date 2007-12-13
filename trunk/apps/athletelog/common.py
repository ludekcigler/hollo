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

import os
import re
import calendar
import datetime
import itertools

import django.db.models
from django.db.models.query import QuerySet
from django.core.serializers import serialize
from django.utils import simplejson

"""
Miscellaneous utility functions
"""

def week_numbers_in_month(year, month):
    """
    Return list of ISO week numbers for given month
    """
    day = 1
    result = []
    for week_day in calendar.monthcalendar(year, month):
        yield datetime.date(year, month, day).isocalendar()[1]
        day += (7 - datetime.date(year, month, day).isocalendar()[2] + 1)

def iso_week_gregorian_days(year, week):
    """
    Returns a list of dates of a week given by its ISO 8601:1988 week number
    """
    # Determine the first monday
    c = datetime.date(year, 1, 1).isocalendar()
    if c[1] == 1:
        current_year = year - 1
        current_month = 12
        current_day = calendar.monthrange(current_year, current_month)[1] - c[2] + 2
    else:
        current_year = year
        current_month = 1
        current_day = 7 - c[2] + 2

    for current_week in xrange(1, week):
        # Compute next monday
        current_day += 7
        current_year, current_month, current_day = adjust_date(current_year, current_month, current_day)

    # Iterate over all week days
    for day_of_week in xrange(0, 7):
        y, m, d = adjust_date(current_year, current_month, current_day + day_of_week)
        yield datetime.date(y, m, d)

def iso_week_day_to_gregorian(year, week, day_of_week):
    """
    Convert ISO 8601:1988 week day to gregorian date
    """
    return list(itertools.islice(iso_week_gregorian_days(year, week), day_of_week - 1, day_of_week))[0]

def adjust_date(year, month, day):
    """
    Helper function for iso_week_day_to_gregorian

    Adjusts the date is the day is greater than number of days in the month
    """
    if day > calendar.monthrange(year, month)[1]:
        day = day - calendar.monthrange(year, month)[1]
        month = month + 1
        if month > 12:
            year = year + 1
            month = 1
    return year, month, day


def next_month(year, month):
    if month == 12:
        return year + 1, 1
    else:
        return year, month + 1

def previous_month(year, month):
    if month == 1:
        return year - 1, 12
    else:
        return year, month - 1

def get_unique_filename(dir, filename):
    """
    Gets unique filename which is not present in the directory at the moment
    """
    while (os.path.exists(os.path.abspath(os.path.join(dir, filename)))):
        filename = '_%s' % filename

    return filename

def get_submit_button(postContents):
    """
    Determine submit button in the HTTP POST contents
    """
    for key in postContents:
        m = re.match('^submit_([^\.]*).*$', key)
        if m:
            return m.group(1)
    return None


from django.core.serializers import json
import types

class AthleteLogJSONEncoder(json.DateTimeAwareJSONEncoder):
    def default(self, obj):
        if 'jsonify' in dir(obj):
            return obj.jsonify()
        elif isinstance(obj, django.db.models.Model):
            return unicode(obj)
        elif not obj:
            return []
        else:
            return json.DateTimeAwareJSONEncoder.default(self, obj)

def jsonify(object):
    if isinstance(object, QuerySet):
        return serialize('json', object)
    return simplejson.dumps(object, cls=AthleteLogJSONEncoder)
