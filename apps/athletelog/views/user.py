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
User's administration views for the athlete log application
"""

import urllib2

import django.contrib.auth
from django import http 
from django.shortcuts import render_to_response
from django.template import loader, Context, RequestContext
from django.core.urlresolvers import reverse

from athletelog import views

def login(request):
    t = loader.get_template('athletelog/login.html')
    context = {}
    if request.GET.has_key('continue'):
        context['continue_url'] = request.GET['continue']
    if request.GET.has_key('auth') and request.GET['auth']:
        context['login_failed'] = True
    c = RequestContext(request, context)
    return http.HttpResponse(t.render(c))


def auth(request):
    username = request.POST['username']
    password = request.POST['password']
    
    user = django.contrib.auth.authenticate(username=username, password=password)
    continue_url = request.GET.has_key('continue') and request.GET['continue']
    if user is not None and user.is_active:
        django.contrib.auth.login(request, user)
        return http.HttpResponseRedirect(continue_url or reverse('athletelog.views.index'))
    else:
        query_string = 'auth=error'
        if continue_url:
            query_string += ('&continue=%s' % urllib2.quote(continue_url))
        return http.HttpResponseRedirect("%s?%s" % (reverse('athletelog.views.user.login'), query_string))


def logout(request):
    django.contrib.auth.logout(request)
    return views.index(request)
