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
DB models for Hollo
"""

import re

from django.db import models

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

PERSON_IMAGE_UPLOAD_DIR = 'avatars'
TRACK_EVENT_RESULT_TYPE_CHOICES = (('T', 'Time'), ('L', 'Length'), ('P', 'Points'), )
WORKOUT_TYPE_NUM_CHOICES = (('DISTANCE', 'Km'), ('WEIGHT', 'Kg'), ('TIME', 'Min'), ('COUNT', 'Počet'), ('NONE', 'None'))

TIME_RESULT_PATTERN = re.compile('^((?P<h>\d{1,}):(?=\d{1,2}:))?((?P<min>\d{1,2}):)?(?P<sec>\d{1,2})([,\.](?P<msec>\d{1,2}))?$')
DISTANCE_RESULT_PATTERN = re.compile('^((?P<km>\d+)[\.,](?=\d+[\.,]))?((?P<m>\d+)[\.,])?(?P<cm>\d+)$')
POINTS_RESULT_PATTERN = re.compile('^(?P<pt>\d+)$')

class Person(models.Model):
    """
    Single user of the log
    """
    user = models.OneToOneField(User)
    # An avatar of the user
    image = models.FileField(upload_to=PERSON_IMAGE_UPLOAD_DIR, blank=True, null=True)
    # List of athletes which the person is allowed to watch
    watched_athletes = models.ManyToManyField('Athlete', related_name='watching_persons', blank=True)

    def __unicode__(self):
        return self.full_name

    def _get_full_name(self):
        if self.user.first_name and self.user.last_name:
            return u'%s %s' % (self.user.first_name, self.user.last_name)
        else:
            return unicode(self.user)

    full_name = property(_get_full_name, doc = 'Full name of the Athlete')
    id = property(lambda self: self.user.id, doc='Id of the underlying user')

    def allowed_athletes(self):
        """
        Returns list of athletes which the person is authorized to view
        """
        retval = set(self.watched_athletes.all())
        retval.update(Athlete.objects.filter(group__coaches__person=self))
        retval.update(Athlete.objects.filter(person=self))
        return list(retval)

    def get_view_status(self, person):
        """
        Gets the status of an athlete with respect to a person
        (is the athlete watched by the person, does he watch a person etc.)
        """

        view_status = {}
        view_status['watching'] = (Athlete.objects.filter(watching_persons=self, person=person).count() > 0)
        view_status['auth_request_from'] = (AuthorizationRequest.objects.filter( \
                        person=person, athlete__person=self).count() > 0)
        view_status['auth_request_to'] = (AuthorizationRequest.objects.filter( \
                        person=self, athlete__person=person).count() > 0)
        view_status['blocked'] = (person.blocking_athletes.filter(person=self).count() > 0)
        view_status['blocks'] = (self.blocking_athletes.filter(person=person).count() > 0)
        view_status['coach'] = (Coach.objects.filter(person=person, athletegroups__athletes__person=self).\
                                        count() > 0)
        view_status['watched'] = (Athlete.objects.filter(watching_persons=person, person=self).count() > 0)

        return view_status

    class Admin:
        list_display = ('user',)


class Athlete(models.Model):
    """
    Single athlete
    """
    person = models.OneToOneField(Person)
    # Name of the club
    club = models.CharField(maxlength = 100, blank=True)
    # Group of athletes this person belongs to
    group = models.ForeignKey('AthleteGroup', related_name='athletes', blank=True, null=True)
    # List of persons who are not allowed to request authorization
    # for the athlete
    blocked_persons = models.ManyToManyField('Person', related_name='blocking_athletes', blank=True)

    def __unicode__(self):
        return unicode(self.person)

    def allowed_edit_by(self, user):
        """
        Checks if the athlete is editable by a specified user
        """
        if self.person.user == user:
            return True

        try:
            coach = Coach.objects.get(person__user=user)
            return coach in self.group.coaches.all()
        except ObjectDoesNotExist:
            return False

    def best_result(self, track_event, min_date=None, max_date=None):
        competitions = Competition.objects.filter(athlete=self, event=track_event)

        if min_date:
            competitions = competitions.filter(day__gte=min_date)
        if max_date:
            competitions = competitions.filter(day__lte=max_date)

        try:
            return max(competitions)
        except ValueError:
            return None

    class Admin:
        pass

class Coach(models.Model):
    """
    Coach of an athlete group
    """
    person = models.OneToOneField(Person)

    def athletes(self):
        """
        Returns a list of all athletes that the coach is in charge with
        """
        return Athlete.objects.filter(group__coaches=self)

    def __unicode__(self):
        return unicode(self.person)

    class Admin:
        pass

class AthleteGroup(models.Model):
    """
    Group of athletes
    """
    name = models.CharField(maxlength = 100)
    coaches = models.ManyToManyField('Coach', related_name='athletegroups')

    def __unicode__(self):
        return self.name

    class Admin:
        pass

class AuthorizationRequest(models.Model):
    """
    A request for authorization
    """
    person = models.ForeignKey('Person', related_name='auth_request_from')
    athlete = models.ForeignKey('Athlete', related_name='auth_request_to')
    message = models.CharField(maxlength=160, blank=True, default='')
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "Authorization request from %s to %s" % (self.person, self.athlete)

    class Admin:
        pass

class TrackEvent(models.Model):
    """
    One event on the track (or outside..), e.g. 100m, Javelin etc.
    """
    name = models.CharField(maxlength=30, primary_key=True)
    # Does the event contain additional info? (used for cross-country etc.)
    has_additional_info = models.BooleanField(default=False)
    # Order of results (determines the result pattern)
    result_type = models.CharField(maxlength=1, choices=TRACK_EVENT_RESULT_TYPE_CHOICES, default='T')

    # Ordering of the track events
    order = models.DateField(auto_now_add=True)

    def __unicode__(self):
        return self.name

    # Check if the result matches the expected one
    def check_result(self, result):
        if self.result_type == 'T':
            return bool(TIME_RESULT_PATTERN.match(result))
        elif self.result_type == 'L':
            return bool(DISTANCE_RESULT_PATTERN.match(result))
        elif self.result_type == 'P':
            return bool(POINTS_RESULT_PATTERN.match(result))
        return False
        

    class Admin:
        list_display = ('name', 'result_type')

    class Meta:
        ordering = ['order']

class Competition(models.Model):
    """
    A competition where the athlete took part
    """
    athlete = models.ForeignKey('Athlete')
    day = models.DateField()
    place = models.CharField(maxlength = 100, default='')
    event = models.ForeignKey('TrackEvent')
    # Additional info about an event, in case the event has such
    event_info = models.CharField(maxlength=100, default='')
    result = models.CharField(maxlength=100)
    note = models.TextField(blank=True, default='')

    def __cmp__(self, other):
        """
        Compare two competition results, return NotImplemented if they are not compatible
        """
        if self.event != other.event:
            return NotImplemented

        if self.event.has_additional_info and self.event_info == other.event_info:
            return NotImplemented

        if self.event.result_type == 'T':
            return compare_times(TIME_RESULT_PATTERN.match(self.result).groupdict(),
                                 TIME_RESULT_PATTERN.match(other.result).groupdict())
        elif self.event.result_type == 'L':
            return compare_distances(DISTANCE_RESULT_PATTERN.match(self.result).groupdict(),
                                 DISTANCE_RESULT_PATTERN.match(other.result).groupdict())
        elif self.event.result_type == 'P':
            return compare_points(POINTS_RESULT_PATTERN.match(self.result).groupdict(),
                                 POINTS_RESULT_PATTERN.match(other.result).groupdict())

        return NotImplemented

    class Admin:
        pass

class Workout(models.Model):
    """
    One workout phase; consists of multiple workout items
    """
    day = models.DateField()
    athlete = models.ForeignKey('Athlete')
    weather = models.CharField(maxlength=100, blank=True, default='')
    note = models.TextField(blank=True, default='')
    rating_satisfaction = models.SmallIntegerField(default=3)
    rating_difficulty = models.SmallIntegerField(default=3)

    MIN_RATING = 1
    MAX_RATING = 5

    def __unicode__(self):
        return "%s, %s" % (str(self.athlete), self.day,)

    def _get_total_num_data(self, num_type):
        total = 0
        for item in self.workout_items.all():
            if item.type.num_type == num_type:
                total += item.num_data
        return total

    def _get_total_km(self):
        return self._get_total_num_data('DISTANCE')

    def _get_total_kg(self):
        return self._get_total_num_data('WEIGHT')

    total_km = property(_get_total_km, 'Total km in given workout or None')
    total_kg = property(_get_total_kg, 'Total kg in given workout or None')

    def _get_num_workout_items(self):
        return len(self.workout_items.all())

    num_workout_items = property(_get_num_workout_items, 'Number of workout items in the workout')

    class Admin:
        list_display = ('day', 'athlete', 'weather')

class WorkoutType(models.Model):
    """
    Workout type list
    """
    abbr = models.CharField(maxlength = 10)
    name = models.CharField(maxlength = 30)
    # Type of numeric data associated with the workout (eg. km, kg, minutes, ...)
    num_type = models.CharField(maxlength=8, choices=WORKOUT_TYPE_NUM_CHOICES, default='DISTANCE')
    order = models.DateField(auto_now_add=True)

    def __unicode__(self):
        return self.abbr

    class Admin:
        pass

    class Meta:
        ordering = ['order']

class WorkoutItem(models.Model):
    """
    One workout item; e.g. warm-up, main phase or chill-out
    """
    workout = models.ForeignKey('Workout', related_name='workout_items')
    sequence = models.IntegerField()
    type = models.ForeignKey('WorkoutType', related_name='workout_items')
    desc = models.TextField()
    num_data = models.DecimalField(decimal_places=2, max_digits=10, default=None, blank=True)

    def __unicode__(self):
        return "%s: %s, %s" % (str(self.workout), self.type.abbr, self.desc,)

    class Admin:
        pass

    class Meta:
        pass

################################################################################
#
#    Functions to normalize track event results
#
################################################################################


def normalize_time(time):
    """
    Normalizes time dictionary -- converts values to a single integer time in msec
    - converts string values to int
    - convert ie. 0:63,9 to 1:03,90
    """
    # This adjusts msec on one decimal point to two decimal points number
    if time.has_key("msec") and time["msec"] and len(time["msec"]) <= 1:
        time["msec"] = str(int(time["msec"])*10)

    return _normalize_quantity_dict(time, ["msec", "sec", "min", "h"], [100, 60, 60, 60])

def normalize_distance(distance):
    """
    Normalizes distance dictionary -- result is an integer distance in centimeters
    """
    return _normalize_quantity_dict(distance, ["cm", "m", "km"], [100, 100, 100])

def normalize_points(points):
    """
    Normalizes points dictionary -- result is an integer in points
    """
    return _normalize_quantity_dict(points, ["pt"], [1])

def _normalize_quantity_dict(a_quantity, quantity_keys, quantity_div_by):
    """
    Normalizes quantity (time, distance) dictionary
    - converts string values to int
    - convert ie. 0:63,9 to 1:03,90
    """
    quantity = a_quantity.copy()

    for key in quantity_keys:
        if quantity.has_key(key) and quantity[key]:
            quantity[key] = int(quantity[key])
        else:
            quantity[key] = 0

    for i in xrange(0, len(quantity_keys) - 1):
        quantity[quantity_keys[i + 1]] += quantity[quantity_keys[i]] / quantity_div_by[i]
        quantity[quantity_keys[i]] = quantity[quantity_keys[i]] % quantity_div_by[i]

    return quantity

def compare_times(time_a, time_b):
    """
    Compares two times (specified by dictionary with keys ["h", "min", "sec", "msec"])
    """
    return (-1)*_compare_quantity(time_a, time_b, 
                    ["h", "min", "sec", "msec"],
                    normalize_time)

def compare_distances(dist_a, dist_b):
    """
    Compare two distances (specified by dictionary with keys ["km", "m", "cm"])
    """
    return _compare_quantity(dist_a, dist_b, 
                    ["km", "m", "cm"],
                    normalize_distance)

def compare_points(dist_a, dist_b):
    """
    Compare two points (specified by dictionary with keys ["pt"])
    """
    return _compare_quantity(dist_a, dist_b, 
                    ["pt"],
                    normalize_points)

def _compare_quantity(quantity_a, quantity_b, quantity_keys, quantity_normalizator):
    quantity_a = quantity_normalizator(quantity_a)
    quantity_b = quantity_normalizator(quantity_b)

    for key in quantity_keys:
        if quantity_a[key] < quantity_b[key]:
            return -1
        elif quantity_a[key] > quantity_b[key]:
            return 1
    return 0

def _tests():
    # normalize_time tests
    time = '4:08,7'
    time_result = TIME_RESULT_PATTERN.match(time).groupdict()
    print 'athletelog.models.normalize_time, %s, %s' % (time, normalize_time(time_result))

    time = '8.63'
    time_result = TIME_RESULT_PATTERN.match(time).groupdict()
    print 'athletelog.models.normalize_time, %s, %s' % (time, normalize_time(time_result))

    # compare_time tests
    time_a = '63.76'
    time_b = '1:04,5'
    print 'athletelog.models.compare_times %s, %s: %s' % (time_a, time_b, 
                    compare_times(TIME_RESULT_PATTERN.match(time_a).groupdict(), TIME_RESULT_PATTERN.match(time_b).groupdict()))

    time_a = '63.76'
    time_b = '1:03,76'
    print 'athletelog.models.compare_times %s, %s: %s' % (time_a, time_b, 
                    compare_times(TIME_RESULT_PATTERN.match(time_a).groupdict(), TIME_RESULT_PATTERN.match(time_b).groupdict()))

    time_a = '63.77'
    time_b = '1:03,76'
    print 'athletelog.models.compare_times %s, %s: %s' % (time_a, time_b, 
                    compare_times(TIME_RESULT_PATTERN.match(time_a).groupdict(), TIME_RESULT_PATTERN.match(time_b).groupdict()))

    # normalize_distance tests
    dist = '2.6.58'
    dist_result = DISTANCE_RESULT_PATTERN.match(dist).groupdict()
    print dist_result
    print 'athletelog.models.normalize_distance, %s, %s' % (dist, normalize_distance(dist_result))

    # compare_distances tests
    dist_a = '2.63.77'
    dist_b = '2.63.76'
    print 'athletelog.models.compare_distances %s, %s: %s' % (dist_a, dist_b, 
                    compare_distances(DISTANCE_RESULT_PATTERN.match(dist_a).groupdict(), DISTANCE_RESULT_PATTERN.match(dist_b).groupdict()))

    # normalize_points tests
    points = '6589'
    points_result = POINTS_RESULT_PATTERN.match(points).groupdict()
    print 'athletelog.models.normalize_points, %s, %s' % (points, normalize_points(points_result))

    # compare_points tests
    points_a = '6377'
    points_b = '6376'
    print 'athletelog.models.compare_points %s, %s: %s' % (points_a, points_b, 
                    compare_points(POINTS_RESULT_PATTERN.match(points_a).groupdict(), POINTS_RESULT_PATTERN.match(points_b).groupdict()))

    print bool(DISTANCE_RESULT_PATTERN.match('4.86'))
