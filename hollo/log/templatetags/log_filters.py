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
    return (int(value) > int(arg))


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
