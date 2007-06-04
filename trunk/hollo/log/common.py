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

import calendar
import datetime
import itertools

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

if __name__ == "__main__":
    for d in xrange(1, 8):
        print iso_week_day_to_gregorian(2002, 14, d)
