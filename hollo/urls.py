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
    (r'^login/$', 'hollo.log.views.user.login'),
    (r'^logout/$', 'hollo.log.views.user.logout'),
    (r'^auth/$', 'hollo.log.views.user.auth'),

    (r'^error/(?P<error_code>\d+)/$', 'hollo.log.views.error'),

    (r'^change_athlete/(?P<view_type>workout|competition)/$', 'hollo.log.views.change_athlete'),

    # Site Media - TODO: Odstranit pri nahrani na server
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.join(PROJECT_DIR, 'media')}),
    # Settings views
    (r'^settings/$', 'hollo.log.views.settings.index'),
    (r'^settings/user/$', 'hollo.log.views.settings.user'),
    (r'^settings/user/change_password/$', 'hollo.log.views.settings.user_change_password'),
    (r'^settings/user/submit_password/$', 'hollo.log.views.settings.user_submit_password'),
    (r'^settings/user/remove_image/$', 'hollo.log.views.settings.user_remove_image'),
    (r'^settings/user/edit_image/$', 'hollo.log.views.settings.user_edit_image'),
    (r'^settings/user/upload_image/$', 'hollo.log.views.settings.user_upload_image'),
    (r'^settings/my_athletes/$', 'hollo.log.views.settings.my_athletes'),
    (r'^settings/friends/$', 'hollo.log.views.settings.friends'),
    (r'^settings/friends/add/$', 'hollo.log.views.settings.friends_add'),
    (r'^settings/friends/add/(?P<athlete_id>\w+)/$', 'hollo.log.views.settings.friends_add_edit_message'),
    (r'^settings/friends/add_submit/(?P<athlete_id>\w+)/$', 'hollo.log.views.settings.friends_add_submit'),
    (r'^settings/friends/remove/(?P<athlete_id>\w+)/$', 'hollo.log.views.settings.friends_remove'),
    (r'^settings/friends/block/(?P<person_id>\w+)/$', 'hollo.log.views.settings.friends_block'),
    (r'^settings/friends/unblock/(?P<person_id>\w+)/$', 'hollo.log.views.settings.friends_unblock'),
    (r'^settings/friends/auth/(?P<person_id>\w+)/$', 'hollo.log.views.settings.friends_auth'),
    (r'^settings/friends/auth_reject/(?P<person_id>\w+)/$', 'hollo.log.views.settings.friends_auth_reject'),
    (r'^settings/friends/auth_cancel/(?P<person_id>\w+)/$', 'hollo.log.views.settings.friends_auth_cancel'),
    (r'^settings/friends/auth_list/$', 'hollo.log.views.settings.friends_auth_list'),

    # Personal URLs
    (r'^workout/(?P<athlete_id>\w+)/$', 'hollo.log.views.workout.index'),

    (r'^workout/(?P<athlete_id>\w+)/week/(?P<year>\d{4})/(?P<week>\d{,2})/$', 'hollo.log.views.workout.weekly_view'),
    (r'^workout/(?P<athlete_id>\w+)/week/(?P<year>\d{4})/(?P<week>\d{,2})/day/(?P<detail_year>\d{4})/(?P<detail_month>\d{2})/(?P<detail_day>\d{2})/$', 
        'hollo.log.views.workout.weekly_view'),
    (r'^workout/(?P<athlete_id>\w+)/month/(?P<year>\d{4})/(?P<month>\d{2})/$', 'hollo.log.views.workout.monthly_view'),
    (r'^workout/(?P<athlete_id>\w+)/month/(?P<year>\d{4})/(?P<month>\d{2})/(?P<detail_day>\d{2})/$', 'hollo.log.views.workout.monthly_view'),

    (r'^workout/(?P<athlete_id>\w+)/add_submit/$', 'hollo.log.views.workout.add_submit'),
    (r'^workout/(?P<athlete_id>\w+)/edit_submit/$', 'hollo.log.views.workout.edit_submit'),
    (r'^workout/(?P<athlete_id>\w+)/remove/(?P<workout_id>\d+)/$', 'hollo.log.views.workout.remove_workout'),
    (r'^workout/(?P<athlete_id>\w+)/add/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$', 'hollo.log.views.workout.add_form'),
    (r'^workout/(?P<athlete_id>\w+)/edit/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<workout_id>\d+)/$', 'hollo.log.views.workout.edit_form'),

    (r'^workout/(?P<athlete_id>\w+)/change_view/$', 'hollo.log.views.workout.change_view'),

    (r'^competition/(?P<athlete_id>\w+)/$', 'hollo.log.views.competition.index'),
    (r'^competition/(?P<athlete_id>\w+)/add_submit/$', 'hollo.log.views.competition.add_form'),
    (r'^competition/(?P<athlete_id>\w+)/edit_submit/$', 'hollo.log.views.competition.edit_form'),

    (r'^competition/(?P<athlete_id>\w+)/remove/(?P<competition_id>\d+)/$', 'hollo.log.views.competition.remove_competition'),

    (r'^competition/(?P<athlete_id>\w+)/month/(?P<year>\d{4})/(?P<month>\d{2})/$', 'hollo.log.views.competition.monthly_view'),
    (r'^competition/(?P<athlete_id>\w+)/month/(?P<year>\d{4})/(?P<month>\d{2})/(?P<competition_id>\d+)/$',
        'hollo.log.views.competition.monthly_view'),

    (r'^competition/(?P<athlete_id>\w+)/year/(?P<year>\d{4})/$', 'hollo.log.views.competition.yearly_view'),
    (r'^competition/(?P<athlete_id>\w+)/year/(?P<year>\d{4})/(?P<competition_id>\d+)/$', 
        'hollo.log.views.competition.yearly_view'),

    (r'^competition/(?P<athlete_id>\w+)/change_view/$', 'hollo.log.views.competition.change_view'),

    (r'^competition/(?P<athlete_id>\w+)/add/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$', 'hollo.log.views.competition.add_form'),
    (r'^competition/(?P<athlete_id>\w+)/edit/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<competition_id>\d+)/$', 'hollo.log.views.competition.edit_form'),

    # Ajax methods
    (r'^ajax/workout/add/$', 'hollo.log.views.workout_add_ajax'),
    (r'^ajax/workout/info/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$', \
        'hollo.log.views.workout_info_ajax'),
    (r'^ajax/workout/add_form/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$', \
        'hollo.log.views.workout_add_form'),
    (r'^ajax/workout/edit_form/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<workout_id>\d+)/$', \
        'hollo.log.views.workout_edit_form'),
    (r'^ajax/competition/add_form/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$', \
        'hollo.log.views.competition_add_form'),
    (r'^ajax/competition/edit_form/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<workout_id>\d+)/$', \
        'hollo.log.views.workout_edit_form'),
)
