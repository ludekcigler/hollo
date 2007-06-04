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

import os
from settings import PROJECT_DIR

from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Example:
    # (r'^hollo/', include('hollo.foo.urls')),
    (r'^$', 'hollo.log.views.index'),

    # Uncomment this for admin:
    (r'^admin/', include('django.contrib.admin.urls')),

    # log URL
    (r'^log/$', 'hollo.log.views.index'),
    (r'^log/login/$', 'hollo.log.views.athlete_login'),
    (r'^log/logout/$', 'hollo.log.views.athlete_logout'),
    (r'^log/auth/$', 'hollo.log.views.athlete_auth'),

    (r'^log/workout/week/(?P<year>\d{4})/(?P<week>\d{2})/$', 'hollo.log.views.workout_view_week'),
    (r'^log/workout/week/(?P<year>\d{4})/(?P<week>\d{2})/day/(?P<detail_year>\d{4})/(?P<detail_month>\d{2})/(?P<detail_day>\d{2})/$', 
        'hollo.log.views.workout_view_week'),
    (r'^log/workout/month/(?P<year>\d{4})/(?P<month>\d{2})/$', 'hollo.log.views.workout_view_month'),
    (r'^log/workout/month/(?P<year>\d{4})/(?P<month>\d{2})/(?P<detail_day>\d{2})/$', 'hollo.log.views.workout_view_month'),

    (r'^log/workout/add_submit/$', 'hollo.log.views.workout_add_submit'),
    (r'^log/workout/edit_submit/$', 'hollo.log.views.workout_edit_submit'),
    (r'^log/workout/remove/(?P<workout_id>\d+)/$', 'hollo.log.views.workout_remove'),
    (r'^log/workout/add/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$', 'hollo.log.views.workout_add_form'),
    (r'^log/workout/edit/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<workout_id>\d+)/$', 'hollo.log.views.workout_edit_form'),

    (r'^log/workout/change_view/$', 'hollo.log.views.workout_change_view'),

    (r'^log/competition/add/$', 'hollo.log.views.competition_add'),
    (r'^log/competition/edit/$', 'hollo.log.views.competition_edit'),

    (r'^log/competition/remove/(?P<competition_id>\d+)/$', 'hollo.log.views.competition_remove'),

    (r'^log/competition/month/(?P<year>\d{4})/(?P<month>\d{2})/$', 'hollo.log.views.competition_view_month'),
    (r'^log/competition/month/(?P<year>\d{4})/(?P<month>\d{2})/(?P<competition_id>\d+)/$',
        'hollo.log.views.competition_view_month'),

    (r'^log/competition/year/(?P<year>\d{4})/$', 'hollo.log.views.competition_view_year'),
    (r'^log/competition/year/(?P<year>\d{4})/(?P<competition_id>\d+)/$', 
        'hollo.log.views.competition_view_year'),

    (r'^log/competition/change_view/$', 'hollo.log.views.competition_change_view'),

    (r'^log/competition/add/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$', 'hollo.log.views.competition_add_form'),
    (r'^log/competition/edit/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<competition_id>\d+)/$', 'hollo.log.views.competition_edit_form'),

    # Ajax methods
    (r'^log/ajax/workout/add/$', 'hollo.log.views.workout_add_ajax'),
    (r'^log/ajax/workout/info/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$', \
        'hollo.log.views.workout_info_ajax'),
    (r'^log/ajax/workout/add_form/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$', \
        'hollo.log.views.workout_add_form'),
    (r'^log/ajax/workout/edit_form/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<workout_id>\d+)/$', \
        'hollo.log.views.workout_edit_form'),
    (r'^log/ajax/competition/add_form/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$', \
        'hollo.log.views.competition_add_form'),
    (r'^log/ajax/competition/edit_form/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<workout_id>\d+)/$', \
        'hollo.log.views.workout_edit_form'),

    # Site Media - TODO: Odstranit pri nahrani na server
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.join(PROJECT_DIR, 'media')}),
)
