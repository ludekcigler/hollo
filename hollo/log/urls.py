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

from django.conf.urls.defaults import *

from hollo import log
import log.views
import log.views.competition
import log.views.workout
import log.views.user
import log.views.settings

urlpatterns = patterns('log.views',
    (r'^$', log.views.index),
    (r'^login/$', log.views.user.login),
    (r'^logout/$', log.views.user.logout),
    (r'^auth/$', log.views.user.auth),

    (r'^error/(?P<error_code>\d+)/$', log.views.error),

    (r'^change_athlete/(?P<view_type>workout|competition)/$', log.views.change_athlete),

    # Settings views
    (r'^settings/$', log.views.settings.index),
    (r'^settings/user/$', log.views.settings.user),
    (r'^settings/user/change_password/$', log.views.settings.user_change_password),
    (r'^settings/user/remove_image/$', log.views.settings.user_remove_image),
    (r'^settings/user/edit_image/$', log.views.settings.user_edit_image),
    (r'^settings/user/upload_image/$', log.views.settings.user_upload_image),
    (r'^settings/my_athletes/$', log.views.settings.my_athletes),
    (r'^settings/friends/$', log.views.settings.friends),
    (r'^settings/friends/add/$', log.views.settings.friends_add),
    (r'^settings/friends/add/(?P<athlete_id>\w+)/$', log.views.settings.friends_add_edit_message),
    (r'^settings/friends/add_submit/(?P<athlete_id>\w+)/$', log.views.settings.friends_add_submit),
    (r'^settings/friends/remove/(?P<athlete_id>\w+)/$', log.views.settings.friends_remove),
    (r'^settings/friends/block/(?P<person_id>\w+)/$', log.views.settings.friends_block),
    (r'^settings/friends/unblock/(?P<person_id>\w+)/$', log.views.settings.friends_unblock),
    (r'^settings/friends/auth/(?P<person_id>\w+)/$', log.views.settings.friends_auth),
    (r'^settings/friends/auth_reject/(?P<person_id>\w+)/$', log.views.settings.friends_auth_reject),
    (r'^settings/friends/auth_cancel/(?P<person_id>\w+)/$', log.views.settings.friends_auth_cancel),
    (r'^settings/friends/auth_list/$', log.views.settings.friends_auth_list),

    # Workout
    (r'workout/(?P<athlete_id>\w+)/$', log.views.workout.index),

    (r'^workout/(?P<athlete_id>\w+)/week/(?P<year>\d{4})/(?P<week>\d{,2})/$', log.views.workout.weekly_view),
    (r'^workout/(?P<athlete_id>\w+)/week/(?P<year>\d{4})/(?P<week>\d{,2})/day/(?P<detail_year>\d{4})/(?P<detail_month>\d{,2})/(?P<detail_day>\d{,2})/$', 
        log.views.workout.weekly_view_detail),
    (r'^workout/(?P<athlete_id>\w+)/month/(?P<year>\d{4})/(?P<month>\d{,2})/$', log.views.workout.monthly_view),
    (r'^workout/(?P<athlete_id>\w+)/month/(?P<year>\d{4})/(?P<month>\d{,2})/(?P<detail_day>\d{,2})/$', log.views.workout.monthly_view_detail),

    (r'^workout/(?P<athlete_id>\w+)/add_submit/$', log.views.workout.add_submit),
    (r'^workout/(?P<athlete_id>\w+)/edit_submit/$', log.views.workout.edit_submit),
    (r'^workout/(?P<athlete_id>\w+)/remove/(?P<workout_id>\d+)/$', log.views.workout.remove_workout),
    (r'^workout/(?P<athlete_id>\w+)/add/(?P<year>\d{4})/(?P<month>\d{,2})/(?P<day>\d{,2})/$', log.views.workout.add_form),
    (r'^workout/(?P<athlete_id>\w+)/edit/(?P<year>\d{4})/(?P<month>\d{,2})/(?P<day>\d{,2})/(?P<workout_id>\d+)/$', log.views.workout.edit_form),

    (r'^workout/(?P<athlete_id>\w+)/change_view/$', log.views.workout.change_view),

    # Competition
    (r'^competition/(?P<athlete_id>\w+)/$', log.views.competition.index),
    (r'^competition/(?P<athlete_id>\w+)/add_submit/$', log.views.competition.add_submit),
    (r'^competition/(?P<athlete_id>\w+)/edit_submit/$', log.views.competition.edit_submit),

    (r'^competition/(?P<athlete_id>\w+)/remove/(?P<competition_id>\d+)/$', log.views.competition.remove_competition),

    (r'^competition/(?P<athlete_id>\w+)/month/(?P<year>\d{4})/(?P<month>\d{,2})/$', log.views.competition.monthly_view),
    (r'^competition/(?P<athlete_id>\w+)/month/(?P<year>\d{4})/(?P<month>\d{,2})/(?P<competition_id>\d+)/$',
        log.views.competition.monthly_view),

    (r'^competition/(?P<athlete_id>\w+)/year/(?P<year>\d{4})/$', log.views.competition.yearly_view),
    (r'^competition/(?P<athlete_id>\w+)/year/(?P<year>\d{4})/(?P<competition_id>\d+)/$', 
        log.views.competition.yearly_view),

    (r'^competition/(?P<athlete_id>\w+)/change_view/$', log.views.competition.change_view),

    (r'^competition/(?P<athlete_id>\w+)/add/(?P<year>\d{4})/(?P<month>\d{,2})/(?P<day>\d{,2})/$', log.views.competition.add_form),
    (r'^competition/(?P<athlete_id>\w+)/edit/(?P<year>\d{4})/(?P<month>\d{,2})/(?P<day>\d{,2})/(?P<competition_id>\d+)/$', log.views.competition.edit_form),

    # Javascript-generating views
    (r'^js/event_info/', log.views.js_event_info),
    (r'^js/workout_type_info/', log.views.js_workout_type_info),
)
