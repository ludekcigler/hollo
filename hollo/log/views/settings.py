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

import re
import os
import urllib

import django
from django.template import loader, Context, RequestContext
from django.core.exceptions import ObjectDoesNotExist
from django import http 

from hollo.log import views
from hollo.log.views import login_required
from hollo.log import models
from hollo.log import common
from hollo.settings import MEDIA_ROOT

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
    submit_button = common.get_submit_button(request.POST)
    if submit_button == 'Cancel':
        # Go to redirection page
        return http.HttpResponseRedirect('/')

    person = models.Person.objects.get(user=request.user)
    athlete = models.Athlete.objects.filter(person__user=request.user).count() == 1 and \
                models.Athlete.objects.get(person__user=request.user) or None
    coach = models.Coach.objects.filter(person__user=request.user).count() == 1 and \
                models.Coach.objects.get(person__user=request.user) or None

    if submit_button == 'Ok':
        # The content was already submitted
        person.user.first_name = request.POST['firstName']
        person.user.last_name = request.POST['lastName']

        try: django.core.validators.isValidEmail(request.POST['email'], request.POST)
        except django.core.validators.ValidationError: return http.HttpResponseNotFound()
        person.user.email = request.POST['email']

        if athlete:
            athlete.club = request.POST['club']
            try:
                athlete.group = models.AthleteGroup.objects.get(id=int(request.POST['group']))
            except ObjectDoesNotExist:
                athlete.group = None

            athlete.save()
        
        person.save()
        person.user.save()
        return http.HttpResponseRedirect('/settings/user/')

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
    try:
        # Remove old file
        os.remove(person.get_image_filename())
    except OSError:
        # TODO: redirect to error page
        pass

    person.image = None
    person.save()

    return http.HttpResponseRedirect(request.META.get('HTTP_REFERER', '/settings/user/'))

@login_required
def user_edit_image(request):
    """
    Show edit image form
    """
    context = RequestContext(request, {'continue': request.META.get('HTTP_REFERER', '/settings/user/')})
    tpl = loader.get_template('log/settings_user_edit_image.html')
    return http.HttpResponse(tpl.render(context))

@login_required
def user_upload_image(request):
    """
    Save uploaded image
    """
    redirectUrl = request.REQUEST.has_key('continue') and request.REQUEST['continue'] \
                    or request.META.get('HTTP_REFERER', '/settings/user/')

    submit_button = common.get_submit_button(request.POST)
    if not submit_button or submit_button == 'Cancel' or not request.FILES.has_key('image'):
        # Go to redirection page
        return http.HttpResponseRedirect(redirectUrl)

    image = request.FILES['image']
    person = models.Person.objects.get(user=request.user)
    # Check the MIME type of the uploaded file
    if not re.match('^image/(jpeg|gif|png)$', image['content-type']):
        # TODO: redirect to correct error page
        return None

    try:
        # Write new file
        image_directory = os.path.abspath(os.path.join(MEDIA_ROOT, models.PERSON_IMAGE_UPLOAD_DIR))
        image_filename = common.get_unique_filename(image_directory, image['filename'])

        image_file = open(os.path.abspath(os.path.join(image_directory, image_filename)), 'wb')
        image_file.write(image['content'])
        image_file.close()
    except IOError:
        # TODO: redirect to error page
        raise

    try:
        # Remove old file
        os.remove(person.get_image_filename())
    except OSError:
        # TODO: redirect to error page
        pass

    person.image = os.path.join(models.PERSON_IMAGE_UPLOAD_DIR, image_filename)
    person.save()
    
    return http.HttpResponseRedirect(redirectUrl)

@login_required
def user_change_password(request):
    """
    Change password form
    """
    message = request.REQUEST.has_key('message') and request.REQUEST['message'] or None
    context = RequestContext(request, \
                {'continue': request.META.get('HTTP_REFERER', '/settings/user/'), \
                 'message': message})
    tpl = loader.get_template('log/settings_user_edit_password.html')
    return http.HttpResponse(tpl.render(context))

@login_required
def user_submit_password(request):
    """
    Submit new password
    """
    cont = request.REQUEST.has_key('continue') and request.REQUEST['continue'] or ''
    redirectUrl = cont or request.META.get('HTTP_REFERER', '/settings/user/')

    submit_button = common.get_submit_button(request.POST)
    if not submit_button or submit_button == 'Cancel':
        # Go to redirection page
        return http.HttpResponseRedirect(redirectUrl)

    if request.POST['password'] != request.POST['passwordCheck']:
        return http.HttpResponseRedirect('/settings/user/change_password/?continue=%s&message=%s' % \
            (urllib.quote(cont), urllib.quote('Zadaná hesla si neodpovídají')))

    person = models.Person.objects.get(user=request.user)
    person.user.set_password(request.POST['password'])
    person.save()

    return http.HttpResponseRedirect(redirectUrl)

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

    try:
        coach = models.Coach.objects.get(person=person)
    except ObjectDoesNotExist:
        coach = None

    # Load athletes from my group, together with their status

    my_group_athletes = []
    if athlete:
        for ath in athlete.group.athletes.exclude(pk=athlete):
            ath_data = {'athlete': ath, 'view_status': ath.person.get_view_status(athlete.person)}
            my_group_athletes.append(ath_data)

        my_group_athletes.sort(cmp= \
                            (lambda x, y: \
                                cmp(x['athlete'].person.user.last_name, y['athlete'].person.user.last_name) \
                                or \
                                cmp(x['athlete'].person.user.first_name, y['athlete'].person.user.first_name)))

    blocked_persons = []
    if athlete:
        for bp in athlete.blocked_persons.all():
            # If the person does not belong to the same group, show it as blocked
            if not models.Athlete.objects.filter(person=bp, group=athlete.group):
                blocked_persons.append(bp)

    # Other persons
    if athlete:
        watching_persons = models.Person.objects.filter(watched_athletes=athlete)
        auth_req_from = models.Person.objects.filter(auth_request_from__athlete=athlete)
    else:
        watching_persons = []
        auth_req_from = []

    watched_athletes = models.Person.objects.filter(athlete__watching_persons=person)
    auth_req_to = models.Person.objects.filter(athlete__auth_request_to__person=person)
    # Fetch watched athletes
    other_persons_set = set(watching_persons)
    other_persons_set.update(watched_athletes)
    other_persons_set.update(auth_req_from)
    other_persons_set.update(auth_req_to)

    other_persons = []
    other_persons_ids = set()
    for op in other_persons_set:
        try:
            other_athlete = models.Athlete.objects.get(person=op)
        except ObjectDoesNotExist:
            other_athlete = None

        if not models.Athlete.objects.filter(person=op, group=athlete.group) and not op.id in other_persons_ids:
            other_persons_ids.add(op.id)
            other_persons.append({'person': op, 'view_status': op.get_view_status(athlete.person), \
                                  'athlete': other_athlete})

    other_persons.sort(cmp=(lambda x, y: \
                                cmp(x['person'].user.last_name, y['person'].user.last_name) or \
                                cmp(x['person'].user.first_name, y['person'].user.first_name)))

    context = {'person': person,
               'athlete': athlete,
               'coach': coach,
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
    person_watched_athletes = set([a.person_id for a in person.watched_athletes.all()])
    person_watched_athletes.update([req.athlete.person_id for req in person.auth_request_from.all()])
    person_group_athletes = []
    try:
        athlete = models.Athlete.objects.get(person=person)

        person_group_athletes = [a for a in athlete.group.athletes.all() \
                                 if (a != athlete) and (not a.person_id in person_watched_athletes)
                                 and (a.blocked_persons.filter(pk=person).count() == 0)]
        # All other athlete from my group, except those that are not watched and those that do not block me
        person_group_athletes.sort(cmp=(lambda x, y: \
                                cmp(x['person'].person.user.last_name, y['person'].person.user.last_name) or \
                                cmp(x['person'].person.user.first_name, y['person'].person.user.first_name)))

    except ObjectDoesNotExist:
        athlete = None

    # All athletes which are not in my group, are not watched already and do not block me
    person_other_athletes = [a for a in models.Athlete.objects.all() \
                             if (not a in person_group_athletes) and (a != athlete) \
                             and (not a.person_id in person_watched_athletes) \
                             and (a.blocked_persons.filter(pk=person).count() == 0)]

    person_other_athletes.sort(cmp=(lambda x, y: \
                                cmp(x['person'].person.user.last_name, y['person'].person.user.last_name) or \
                                cmp(x['person'].person.user.first_name, y['person'].person.user.first_name)))

    context = {'person': person,
               'athlete': athlete,
               'person_group_athletes': person_group_athletes,
               'person_other_athletes': person_other_athletes}

    tpl = loader.get_template('log/settings_friends_add.html')
    context = RequestContext(request, context)
    return http.HttpResponse(tpl.render(context))

@login_required
def friends_add_edit_message(request, athlete_id):
    """
    Edit message for the authorization request
    """
    person = models.Person.objects.get(user=request.user)
    athlete = models.Athlete.objects.get(person__user__username=athlete_id)

    if athlete.blocked_persons.filter(pk=person).count() > 0:
        # TODO: Not allowed to request authorization
        return None
    context = {'person': person, 'athlete': athlete}
    context = RequestContext(request, context)
    tpl = loader.get_template('log/settings_friends_add_message.html')
    return http.HttpResponse(tpl.render(context))

@login_required
def friends_add_submit(request, athlete_id):
    """
    Handle submit of authorization message
    """
    submit_button = common.get_submit_button(request.POST)
    if submit_button == 'Cancel':
        return http.HttpResponseRedirect('/settings/friends/')

    try:
        req = models.AuthorizationRequest()
        req.person = request.user.person
        req.athlete = models.Athlete.objects.get(person__user__username=athlete_id)
        # Check if the user is not blocked
        if req.athlete.blocked_persons.filter(pk=req.person).count() > 0:
            # TODO: error handling (you are blocked)
            return None
        req.message = request.POST['message']
    except ObjectDoesNotExist:
        # TODO: error handling
        return None

    req.save()
    return http.HttpResponseRedirect('/settings/friends/')

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

@login_required
def friends_auth_list(request):
    submit_button = common.get_submit_button(request.POST)
    cont = request.REQUEST.has_key('continue') and request.REQUEST['continue'] \
           or request.META.get('HTTP_REFERER', '/')
    if submit_button == 'Ok':
        return http.HttpResponseRedirect(cont)

    try:
        athlete = models.Athlete.objects.get(person__user=request.user)
    except ObjectDoesNotExist:
        # TODO: another error handling case...
        return None

    context = {'athlete': athlete, 'continue': cont}
    context = RequestContext(request, context)
    tpl = loader.get_template('log/settings_auth_requests.html')
    return http.HttpResponse(tpl.render(context))

def _remove_auth_request(person, athlete):
    try:
        auth_request = models.AuthorizationRequest.objects.get(person=person, \
                            athlete=athlete)
        auth_request.delete()
    except ObjectDoesNotExist:
        pass
    
