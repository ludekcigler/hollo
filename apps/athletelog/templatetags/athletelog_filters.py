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

from django import template

"""
Custom filters for the Log application
"""

register = template.Library()


@register.filter
def trunc(value, length):
    """
    Truncate the given string to specified length
    """
    return value.decode('utf-8')[:int(length)].encode('utf-8')


@register.filter
def minvalue(value, arg):
    """
    Compute minimum out of value and arg
    """
    return min(int(value), int(arg))


@register.filter
def maxvalue(value, arg):
    """
    Compute maximum out of value and arg
    """
    return max(int(value), int(arg))


@register.filter
def greater_than(value, arg):
    """
    Return boolean indicating whether value is greater than arg
    """
    try:
        return (int(value) > int(arg))
    except TypeError:
        return False


@register.filter
def less_than(value, arg):
    """
    Return boolean indicating whether value is less than arg
    """
    return (int(value) < int(arg))


@register.filter
def is_not(value):
    """
    Returns logical negation
    """
    return not(value)


@register.filter
def range_from(value, lower_bound):
    value, lower_bound = int(value), int(lower_bound)
    return range(lower_bound, value)

@register.filter
def range_to(value, upper_bound):
    value, upper_bound = int(value), int(upper_bound)
    return range(value, upper_bound)

@register.filter
def pluralize_cz(value, format):
    value = int(value)
    format_singular, format_plural_few, format_plural_many = format.split(',')
    if value == 1:
        return format_singular % value
    elif value >= 2 and value <= 4:
        return format_plural_few % value
    else:
        return format_plural_many % value

@register.filter
def trunc_unicode(value, length):
    length = int(length)
    return unicode(value)[0:length]

