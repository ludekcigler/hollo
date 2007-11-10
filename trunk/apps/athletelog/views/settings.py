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
Views for settings adjustments
"""

import re
import os
import urllib

import django
from django.template import loader, Context, RequestContext
from django.core.exceptions import ObjectDoesNotExist
from django import http 
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404

from athletelog import views
from athletelog.views import login_required
from athletelog import models
from athletelog import forms
from athletelog import common
from hollo_settings import MEDIA_ROOT

@login_required
def index(request):
    """
    Default settings URL, just redirects to the proper default screen
    """
    return http.HttpResponseRedirect(reverse('athletelog.views.settings.user'))


@login_required
def user(request):
    """
    Display user-specific settings
    """
    continue_url = reverse('athletelog.views.index')
    submit_button = common.get_submit_button(request.POST)
    if submit_button == 'cancel':
        # Go to redirection page
        return http.HttpResponseRedirect(continue_url)

    person = get_object_or_404(models.Person, user=request.user)
    athlete = models.Athlete.objects.filter(person__user=request.user).count() == 1 and \
                models.Athlete.objects.get(person__user=request.user) or None
    coach = models.Coach.objects.filter(person__user=request.user).count() == 1 and \
                models.Coach.objects.get(person__user=request.user) or None

    context = {'person': person,
               'athlete': athlete,
               'coach': coach,
               'continue': continue_url}

    user_form_groups = [('', '-- Žádná --')]
    user_form_groups.extend([(g.id, g.name) for g in models.AthleteGroup.objects.all()])

    if not submit_button:
        # Default, the content was not submitted
        user_data = {'first_name': person.user.first_name,
                     'last_name': person.user.last_name,
                     'email': person.user.email,
                     'club': athlete and athlete.club or None,
                     'athlete_group': athlete and athlete.group and athlete.group.id or None}

        user_form = forms.SettingsUserForm(user_data, auto_id='user_%s')
        user_form.fields["athlete_group"].choices = user_form_groups
    elif submit_button == 'ok':
        user_form = forms.SettingsUserForm(request.POST, auto_id='user_%s')
        user_form.fields["athlete_group"].choices = user_form_groups

        if user_form.is_valid():
            # Save data for the person
            person.user.first_name = user_form.cleaned_data['first_name']
            person.user.last_name = user_form.cleaned_data['last_name']
            person.user.email = user_form.cleaned_data['email']

            if athlete:
                athlete.club = user_form.cleaned_data['club']
                try:
                    athlete.group = models.AthleteGroup.objects.get(id=user_form.cleaned_data['athlete_group'])
                except ObjectDoesNotExist:
                    athlete.group = None
                athlete.save()
            person.save()
            person.user.save()
            return http.HttpResponseRedirect(continue_url)
        else:
            context['form_errors'] = True

    context['user_form'] = user_form

    tpl = loader.get_template('athletelog/settings_user.html')
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

    return http.HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('athletelog.views.settings.user')))

@login_required
def user_edit_image(request):
    """
    Show edit image form
    """
    image_form = forms.SettingsImageForm(auto_id='user_%s')
    context = {'continue': request.META.get('http_referer', reverse('athletelog.views.settings.user')),
               'image_form': image_form}
    context = RequestContext(request, context)
    tpl = loader.get_template('athletelog/settings_user_edit_image.html')
    return http.HttpResponse(tpl.render(context))

@login_required
def user_upload_image(request):
    """
    Save uploaded image
    """
    continue_url = request.REQUEST.has_key('continue') and request.REQUEST['continue'] \
                    or request.META.get('HTTP_REFERER', reverse('athletelog.views.settings.user'))

    image_form = forms.SettingsImageForm(request.POST, request.FILES, auto_id='user_%s')

    submit_button = common.get_submit_button(request.POST)
    if not submit_button or submit_button == 'cancel' or not image_form.is_valid():
        # Go to redirection page
        return http.HttpResponseRedirect(continue_url)

    image = request.FILES['image']
    person = models.Person.objects.get(user=request.user)
    # Check the MIME type of the uploaded file
    if not re.match('^image/(jpeg|gif|png)$', image['content-type']):
        # TODO: redirect to correct error page
        raise
        return http.HttpResponseRedirect(continue_url)

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
        pass

    person.image = os.path.join(models.PERSON_IMAGE_UPLOAD_DIR, image_filename)
    person.save()
    
    return http.HttpResponseRedirect(continue_url)

@login_required
def user_change_password(request):
    """
    Change password form
    """
    continue_url = request.REQUEST.has_key('continue') and request.REQUEST['continue'] \
                    or request.META.get('HTTP_REFERER', reverse('athletelog.views.settings.user'))

    form_errors = False
    form_error_message = ''
    submit_button = common.get_submit_button(request.POST)
    if not submit_button:
        data = {'password': '', 'password_retype': ''}
        password_form = forms.SettingsPasswordForm(data, auto_id='user_%s')
    elif submit_button == "cancel":
        return http.HttpResponseRedirect(continue_url)
    else:
        password_form = forms.SettingsPasswordForm(request.POST, auto_id='user_%s')
        if password_form.is_valid():
            if password_form.cleaned_data['password'] == password_form.cleaned_data['password_retype']:
                person = models.Person.objects.get(user=request.user)
                person.user.set_password(password_form.cleaned_data['password'])
                person.save()
                return http.HttpResponseRedirect(continue_url)
            else:
                form_error_message = 'Zadaná hesla si neodpovídají'
        else:
            form_errors = True

    context = {'continue': continue_url,
               'password_form': password_form,
               'form_errors': form_errors,
               'form_error_message': form_error_message} 
    context = RequestContext(request, context)
    tpl = loader.get_template('athletelog/settings_user_edit_password.html')
    return http.HttpResponse(tpl.render(context))

@login_required
def my_athletes(request):
    """
    Display settings for coach groups
    """
    try:
        coach = models.Coach.objects.get(person=request.user.id)
    except ObjectDoesNotExist:
        return http.HttpResponseRedirect(reverse('athletelog.views.settings.index'))

    tpl = loader.get_template('athletelog/settings_my_athletes.html')
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
    if athlete and athlete.group:
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
    athlete_group = None
    if athlete:
        watching_persons = models.Person.objects.filter(watched_athletes=athlete)
        auth_req_from = models.Person.objects.filter(auth_request_from__athlete=athlete)
        athlete_group = athlete.group
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

        if not models.Athlete.objects.filter(person=op, group=athlete_group) and not op.id in other_persons_ids:
            other_persons_ids.add(op.id)
            other_persons.append({'person': op, 'view_status': op.get_view_status(person), \
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

    tpl = loader.get_template('athletelog/settings_friends.html')
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

        if athlete.group:
            person_group_athletes = [a for a in athlete.group.athletes.all() \
                                 if (a != athlete) and (not a.person_id in person_watched_athletes)
                                 and (a.blocked_persons.filter(pk=person).count() == 0)]
            # All other athlete from my group, except those that are not watched and those that do not block me
            person_group_athletes.sort(cmp=(lambda x, y: \
                                cmp(x['person'].person.user.last_name, y['person'].person.user.last_name) or \
                                cmp(x['person'].person.user.first_name, y['person'].person.user.first_name)))
        else:
            person_group_athletes = []

    except ObjectDoesNotExist:
        athlete = None

    try:
        coach = models.Coach.objects.get(person=person)
    except ObjectDoesNotExist:
        coach = None

    # All athletes which are not in my group, are not watched already and do not block me
    # and I do not coach them
    person_other_athletes = [a for a in models.Athlete.objects.all() \
                             if (not a in person_group_athletes) and (a != athlete) \
                             and (not a.person_id in person_watched_athletes) \
                             and (a.blocked_persons.filter(pk=person).count() == 0)
                             and (not coach or not a in coach.athletes())]

    person_other_athletes.sort(cmp=(lambda x, y: \
                                cmp(x.person.user.last_name, y.person.user.last_name) or \
                                cmp(x.person.user.first_name, y.person.user.first_name)))

    context = {'person': person,
               'athlete': athlete,
               'coach': coach,
               'person_group_athletes': person_group_athletes,
               'person_other_athletes': person_other_athletes}

    tpl = loader.get_template('athletelog/settings_friends_add.html')
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
    tpl = loader.get_template('athletelog/settings_friends_add_message.html')
    return http.HttpResponse(tpl.render(context))

@login_required
def friends_add_submit(request, athlete_id):
    """
    Handle submit of authorization message
    """
    submit_button = common.get_submit_button(request.POST)
    if submit_button == 'Cancel':
        return http.HttpResponseRedirect(reverse('athletelog.views.settings.friends'))

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
    return http.HttpResponseRedirect(reverse('athletelog.views.settings.friends'))

@login_required
def friends_remove(request, athlete_id):
    person = models.Person.objects.get(user=request.user)
    try:
        athlete = models.Athlete.objects.get(person__user__username=athlete_id)
        person.watched_athletes.remove(athlete)
    except ObjectDoesNotExist:
        pass

    return http.HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('athletelog.views.index')))


@login_required
def friends_auth(request, person_id):
    try:
        athlete = models.Athlete.objects.get(person__user=request.user)
        auth_person = models.Person.objects.get(user__username=person_id)
        _remove_auth_request(auth_person, athlete)
        auth_person.watched_athletes.add(athlete)
    except ObjectDoesNotExist:
        pass

    return http.HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('athletelog.views.index')))

@login_required
def friends_auth_reject(request, person_id):
    try:
        athlete = models.Athlete.objects.get(person__user=request.user)
        auth_person = models.Person.objects.get(user__username=person_id)
        _remove_auth_request(auth_person, athlete)
    except ObjectDoesNotExist:
        pass

    return http.HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('athletelog.views.index')))

@login_required
def friends_auth_cancel(request, athlete_id):
    try:
        auth_athlete = models.Athlete.objects.get(person__user__username=athlete_id)
        person = models.Person.objects.get(user=request.user)
        _remove_auth_request(person, auth_athlete)
    except ObjectDoesNotExist:
        pass

    return http.HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('athletelog.views.index')))


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

    return http.HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('athletelog.views.index')))


@login_required
def friends_unblock(request, person_id):
    try:
        athlete = models.Athlete.objects.get(person__user=request.user)
        unblocked_person = models.Person.objects.get(user__username=person_id)
        athlete.blocked_persons.remove(unblocked_person)
    except ObjectDoesNotExist:
        pass

    return http.HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('athletelog.views.index')))

@login_required
def friends_auth_list(request):
    submit_button = common.get_submit_button(request.POST)
    cont = request.REQUEST.has_key('continue') and request.REQUEST['continue'] \
           or request.META.get('HTTP_REFERER', reverse('athletelog.views.index'))
    if submit_button == 'Ok':
        return http.HttpResponseRedirect(cont)

    try:
        athlete = models.Athlete.objects.get(person__user=request.user)
    except ObjectDoesNotExist:
        # TODO: another error handling case...
        return None

    context = {'athlete': athlete, 'continue': cont}
    context = RequestContext(request, context)
    tpl = loader.get_template('athletelog/settings_auth_requests.html')
    return http.HttpResponse(tpl.render(context))

def _remove_auth_request(person, athlete):
    try:
        auth_request = models.AuthorizationRequest.objects.get(person=person, \
                            athlete=athlete)
        auth_request.delete()
    except ObjectDoesNotExist:
        pass
    
