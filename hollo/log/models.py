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
from django.core.exceptions import ObjectDoesNotExist

PERSON_IMAGE_UPLOAD_DIR = 'avatars'

class Person(models.Model):
    """
    Single user of the log
    """
    user = models.OneToOneField(User)
    # An avatar of the user
    image = models.FileField(upload_to=PERSON_IMAGE_UPLOAD_DIR, blank=True, null=True)
    # List of athletes which the person is allowed to watch
    watched_athletes = models.ManyToManyField('Athlete', related_name='watching_persons', blank=True)

    def __str__(self):
        return self.full_name

    def _get_full_name(self):
        if self.user.first_name and self.user.last_name:
            return "%s %s" % (self.user.first_name, self.user.last_name)
        else:
            return str(self.user)

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
        view_status['blocked'] = (Athlete.objects.filter( \
                        blocked_persons=person, person=self).count() > 0)

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

    def __str__(self):
        return str(self.person)

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

    def __str__(self):
        return str(self.person)

    class Admin:
        pass

class AthleteGroup(models.Model):
    """
    Group of athletes
    """
    name = models.CharField(maxlength = 100)
    coaches = models.ManyToManyField('Coach', related_name='athletegroups')

    def __str__(self):
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

    def __str__(self):
        return "Authorization request from %s to %s" % (self.person, self.athlete)

    class Admin:
        pass

class TrackEvent(models.Model):
    """
    One event on the track (or outside..), e.g. 100m, Javelin etc.
    """
    name = models.CharField(maxlength=30, primary_key=True)
    # Pattern to verify result on server-side (including named groups)
    result_pattern = models.CharField(maxlength=150, default='^.*$')
    # Pattern to verify result on client side (using JS)
    js_result_pattern = models.CharField(maxlength=150, default='^.*$')
    # Order of results
    result_type = models.CharField(maxlength=1,
                    choices=(('T', 'Time'), ('L', 'Length'), ('P', 'Points')))

    # Ordering of the track events
    order = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Admin:
        list_display = ('name', 'result_pattern', 'result_type')

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
    result = models.CharField(maxlength = 100)
    note = models.TextField(blank=True, default='')

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
    rating = models.SmallIntegerField(default=3)

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
    order = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.abbr

    class Admin:
        pass

    class Meta:
        ordering = ['order']

class WorkoutItem(models.Model):
    """
    One workout item; e.g. warm-up, main phase or chill-out
    """
    workout = models.ForeignKey('Workout')
    sequence = models.IntegerField()
    type = models.ForeignKey('WorkoutType')
    desc = models.TextField()
    km = models.FloatField(decimal_places=2, max_digits=5, default=None, blank=True)

    def __str__(self):
        return "%s: %s, %s" % (str(self.workout), self.type.abbr, self.desc,)

    class Admin:
        pass

    class Meta:
        pass
