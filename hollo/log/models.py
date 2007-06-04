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

"""
DB models for Hollo
"""

from django.db import models

from django.contrib.auth.models import User

class Athlete(models.Model):
    """
    Single athlete.
    """
    user = models.OneToOneField(User)
    club = models.CharField(maxlength = 100)

    def __str__(self):
        return self.full_name

    def _get_full_name(self):
        if self.user.first_name and self.user.last_name:
            return "%s %s" % (self.user.first_name, self.user.last_name)
        else:
            return str(self.user)

    full_name = property(_get_full_name, doc = 'Full name of the Athlete')

    class Admin:
        list_display = ('user', 'club')

class AthleteGroup(models.Model):
    """
    Group of athletes
    """
    name = models.CharField(maxlength = 100)
    coach = models.ForeignKey('Athlete', related_name = 'coach')
    athletes = models.ManyToManyField('Athlete')

    class Admin:
        list_display = ('name', 'coach')
        fields = (
                 (None, {'fields': ('name', 'coach', 'athletes')}),
                 )

class TrackEvent(models.Model):
    """
    One event on the track (or outside..), e.g. 100m, Javelin etc.
    """
    name = models.CharField(maxlength = 30, primary_key = True)
    result_pattern = models.CharField(maxlength = 150)
    result_ordering = models.BooleanField(choices = ((False, 'ASC'), (True, 'DESC')))

    def __str__(self):
        return self.name

    class Admin:
        list_display = ('name', 'result_pattern', 'result_ordering')

class Competition(models.Model):
    """
    A competition where the athlete took part
    """
    athlete = models.ForeignKey('Athlete')
    day = models.DateField()
    place = models.CharField(maxlength = 100)
    event = models.ForeignKey('TrackEvent')
    result = models.CharField(maxlength = 100)
    note = models.TextField()

    class Admin:
        pass

class Workout(models.Model):
    """
    One workout phase; consists of multiple workout items
    """
    day = models.DateField()
    athlete = models.ForeignKey('Athlete')
    weather = models.CharField(maxlength=100, blank=True)
    note = models.TextField()

    def __str__(self):
        return "%s, %s" % (str(self.athlete), self.day,)

    def _get_total_km(self):
        try:
            return reduce(lambda x, y: x + y, [v['km'] for v in self.workoutitem_set.values('km')])
        except TypeError:
            return 0

    total_km = property(_get_total_km, 'Total km in given workout')

    def _get_num_workout_items(self):
        return len(self.workoutitem_set.all())

    num_workout_items = property(_get_num_workout_items, 'Number of workout items in the workout')

    class Admin:
        list_display = ('day', 'athlete', 'weather')

class WorkoutType(models.Model):
    """
    Workout type list
    """
    abbr = models.CharField(maxlength = 10)
    name = models.CharField(maxlength = 30)

    def __str__(self):
        return self.abbr

    class Admin:
        pass

class WorkoutItem(models.Model):
    """
    One workout item; e.g. warm-up, main phase or chill-out
    """
    workout = models.ForeignKey('Workout')
    sequence = models.IntegerField()
    type = models.ForeignKey('WorkoutType')
    desc = models.TextField()
    km = models.FloatField(decimal_places = 2, max_digits = 5, default = None, blank = True)

    def __str__(self):
        return "%s: %s, %s" % (str(self.workout), self.type.abbr, self.desc,)

    class Admin:
        pass

    class Meta:
        pass
