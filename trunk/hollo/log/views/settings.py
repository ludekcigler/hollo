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
Views for settings adjustments
"""

from django.template import loader, Context, RequestContext
from django.core.exceptions import ObjectDoesNotExist
from django import http 

from hollo.log import views
from hollo.log.views import login_required
from hollo.log import models
from hollo.log import common

@login_required
def index(request):
    """
    Default settings URL, just redirects to the proper default screen
    """
    return http.HttpResponseRedirect('/settings/user/')


@login_required
def user(request):
    """
    Display user-specific settings
    """
    person = models.Person.objects.get(user=request.user)
    athlete = models.Athlete.objects.filter(person__user=request.user).count() == 1 and \
                models.Athlete.objects.get(person__user=request.user) or None
    coach = models.Coach.objects.filter(person__user=request.user).count() == 1 and \
                models.Coach.objects.get(person__user=request.user) or None

    context = {'person': person, 'athlete': athlete, 'coach': coach}

    tpl = loader.get_template('log/settings_user.html')
    context = RequestContext(request, context)
    return http.HttpResponse(tpl.render(context))

@login_required
def user_remove_image(request):
    """
    Remove image for the user
    """
    person = models.Person.objects.get(user=request.user)
    person.image = None
    person.save()

    return http.HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def my_athletes(request):
    """
    Display settings for coach groups
    """
    try:
        coach = models.Coach.objects.get(person=request.user.id)
    except ObjectDoesNotExist:
        return http.HttpResponseRedirect('/settings/')

    tpl = loader.get_template('log/settings_my_athletes.html')
    context = RequestContext(request, {'coach': coach})
    return http.HttpResponse(tpl.render(context))

@login_required
def friends(request):
    """
    View settings for which people can see your workout logs
    """
    person = models.Person.objects.get(user=request.user)
    try:
        athlete = models.Athlete.objects.get(person=person)
    except ObjectDoesNotExist:
        athlete = None

    # Load athletes from my group, together with their status

    my_group_athletes = []
    for ath in athlete.group.athletes.exclude(pk=athlete):
        ath_data = {'athlete': ath, 'view_status': ath.person.get_view_status(athlete.person)}
        my_group_athletes.append(ath_data)

    blocked_persons = []
    for bp in athlete.blocked_persons.all():
        # If the person does not belong to the same group, show it as blocked
        if not models.Athlete.objects.filter(person=bp, group=athlete.group):
            blocked_persons.append(bp)

    # Other persons
    watching_persons = models.Person.objects.filter(watched_athletes=athlete)
    watched_athletes = models.Person.objects.filter(athlete__watching_persons=athlete.person)
    auth_req_from = models.Person.objects.filter(auth_request_from__athlete=athlete)
    auth_req_to = models.Person.objects.filter(athlete__auth_request_to__person=athlete.person)
    # Fetch watched athletes
    other_persons_set = set(watching_persons)
    other_persons_set.update(watched_athletes)
    other_persons_set.update(auth_req_from)
    other_persons_set.update(auth_req_to)

    other_persons = []
    other_persons_ids = set()
    for op in other_persons_set:
        if not models.Athlete.objects.filter(person=op, group=athlete.group) and not op.id in other_persons_ids:
            other_persons_ids.add(op.id)
            other_persons.append({'person': op, 'view_status': op.get_view_status(athlete.person)})

    context = {'person': person,
               'athlete': athlete,
               'my_group_athletes': my_group_athletes,
               'blocked_persons': blocked_persons,
               'other_persons': other_persons}

    tpl = loader.get_template('log/settings_friends.html')
    context = RequestContext(request, context)
    return http.HttpResponse(tpl.render(context))

@login_required
def friends_add(request):
    """
    Displays an "Add friend" page
    """
    person = models.Person.objects.get(user=request.user)
    tpl = loader.get_template('log/settings_friends_add.html')
    context = RequestContext(request, {'person': person})
    return http.HttpResponse(tpl.render(context))

@login_required
def friends_add_submit(request, athlete_id):
    pass    

@login_required
def friends_remove(request, athlete_id):
    person = models.Person.objects.get(user=request.user)
    try:
        athlete = models.Athlete.objects.get(person__user__username=athlete_id)
        person.watched_athletes.remove(athlete)
    except ObjectDoesNotExist:
        pass

    return http.HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def friends_auth(request, person_id):
    try:
        athlete = models.Athlete.objects.get(person__user=request.user)
        auth_person = models.Person.objects.get(user__username=person_id)
        _remove_auth_request(auth_person, athlete)
        auth_person.watched_athletes.add(athlete)
    except ObjectDoesNotExist:
        pass

    return http.HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def friends_auth_reject(request, person_id):
    try:
        athlete = models.Athlete.objects.get(person__user=request.user)
        auth_person = models.Person.objects.get(user__username=person_id)
        _remove_auth_request(auth_person, athlete)
    except ObjectDoesNotExist:
        pass

    return http.HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def friends_auth_cancel(request, athlete_id):
    try:
        auth_athlete = models.Athlete.objects.get(person__user__username=athlete_id)
        person = models.Person.objects.get(user=request.user)
        _remove_auth_request(person, auth_athlete)
    except ObjectDoesNotExist:
        pass

    return http.HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def friends_block(request, person_id):
    try:
        athlete = models.Athlete.objects.get(person__user=request.user)
        blocked_person = models.Person.objects.get(user__username=person_id)
        blocked_person.watched_athletes.remove(athlete)
        athlete.blocked_persons.add(blocked_person)

        _remove_auth_request(blocked_person, athlete)
    except ObjectDoesNotExist:
        pass

    return http.HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def friends_unblock(request, person_id):
    try:
        athlete = models.Athlete.objects.get(person__user=request.user)
        unblocked_person = models.Person.objects.get(user__username=person_id)
        athlete.blocked_persons.remove(unblocked_person)
    except ObjectDoesNotExist:
        pass

    return http.HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def _remove_auth_request(person, athlete):
    try:
        auth_request = models.AuthorizationRequest.objects.get(person=person, \
                            athlete=athlete)
        auth_request.delete()
    except ObjectDoesNotExist:
        pass
    
