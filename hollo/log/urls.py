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

urlpatterns = patterns('log.views',
    (r'^$', 'index'),
    (r'^login/$', 'user.login'),
    (r'^logout/$', 'user.logout'),
    (r'^auth/$', 'user.auth'),

    (r'^error/(?P<error_code>\d+)/$', 'error'),

    (r'^change_athlete/(?P<view_type>workout|competition)/$', 'change_athlete'),

    # Settings views
    (r'^settings/$', 'settings.index'),
    (r'^settings/user/$', 'settings.user'),
    (r'^settings/user/change_password/$', 'settings.user_change_password'),
    (r'^settings/user/remove_image/$', 'settings.user_remove_image'),
    (r'^settings/user/edit_image/$', 'settings.user_edit_image'),
    (r'^settings/user/upload_image/$', 'settings.user_upload_image'),
    (r'^settings/my_athletes/$', 'settings.my_athletes'),
    (r'^settings/friends/$', 'settings.friends'),
    (r'^settings/friends/add/$', 'settings.friends_add'),
    (r'^settings/friends/add/(?P<athlete_id>\w+)/$', 'settings.friends_add_edit_message'),
    (r'^settings/friends/add_submit/(?P<athlete_id>\w+)/$', 'settings.friends_add_submit'),
    (r'^settings/friends/remove/(?P<athlete_id>\w+)/$', 'settings.friends_remove'),
    (r'^settings/friends/block/(?P<person_id>\w+)/$', 'settings.friends_block'),
    (r'^settings/friends/unblock/(?P<person_id>\w+)/$', 'settings.friends_unblock'),
    (r'^settings/friends/auth/(?P<person_id>\w+)/$', 'settings.friends_auth'),
    (r'^settings/friends/auth_reject/(?P<person_id>\w+)/$', 'settings.friends_auth_reject'),
    (r'^settings/friends/auth_cancel/(?P<person_id>\w+)/$', 'settings.friends_auth_cancel'),
    (r'^settings/friends/auth_list/$', 'settings.friends_auth_list'),

    # Workout
    (r'workout/(?P<athlete_id>\w+)/$', 'workout.index'),

    (r'^workout/(?P<athlete_id>\w+)/week/(?P<year>\d{4})/(?P<week>\d{,2})/$', 'workout.weekly_view'),
    (r'^workout/(?P<athlete_id>\w+)/week/(?P<year>\d{4})/(?P<week>\d{,2})/day/(?P<detail_year>\d{4})/(?P<detail_month>\d{,2})/(?P<detail_day>\d{,2})/$', 
        'workout.weekly_view_detail'),
    (r'^workout/(?P<athlete_id>\w+)/month/(?P<year>\d{4})/(?P<month>\d{,2})/$', 'workout.monthly_view'),
    (r'^workout/(?P<athlete_id>\w+)/month/(?P<year>\d{4})/(?P<month>\d{,2})/(?P<detail_day>\d{,2})/$', 'workout.monthly_view_detail'),

    (r'^workout/(?P<athlete_id>\w+)/add_submit/$', 'workout.add_submit'),
    (r'^workout/(?P<athlete_id>\w+)/edit_submit/$', 'workout.edit_submit'),
    (r'^workout/(?P<athlete_id>\w+)/remove/(?P<workout_id>\d+)/$', 'workout.remove_workout'),
    (r'^workout/(?P<athlete_id>\w+)/add/(?P<year>\d{4})/(?P<month>\d{,2})/(?P<day>\d{,2})/$', 'workout.add_form'),
    (r'^workout/(?P<athlete_id>\w+)/edit/(?P<year>\d{4})/(?P<month>\d{,2})/(?P<day>\d{,2})/(?P<workout_id>\d+)/$', 'workout.edit_form'),

    (r'^workout/(?P<athlete_id>\w+)/change_view/$', 'workout.change_view'),

    # Competition
    (r'^competition/(?P<athlete_id>\w+)/$', 'competition.index'),
    (r'^competition/(?P<athlete_id>\w+)/add_submit/$', 'competition.add_submit'),
    (r'^competition/(?P<athlete_id>\w+)/edit_submit/$', 'competition.edit_submit'),

    (r'^competition/(?P<athlete_id>\w+)/remove/(?P<competition_id>\d+)/$', 'competition.remove_competition'),

    (r'^competition/(?P<athlete_id>\w+)/month/(?P<year>\d{4})/(?P<month>\d{,2})/$', 'competition.monthly_view'),
    (r'^competition/(?P<athlete_id>\w+)/month/(?P<year>\d{4})/(?P<month>\d{,2})/(?P<competition_id>\d+)/$',
        'competition.monthly_view'),

    (r'^competition/(?P<athlete_id>\w+)/year/(?P<year>\d{4})/$', 'competition.yearly_view'),
    (r'^competition/(?P<athlete_id>\w+)/year/(?P<year>\d{4})/(?P<competition_id>\d+)/$', 
        'competition.yearly_view'),

    (r'^competition/(?P<athlete_id>\w+)/change_view/$', 'competition.change_view'),

    (r'^competition/(?P<athlete_id>\w+)/add/(?P<year>\d{4})/(?P<month>\d{,2})/(?P<day>\d{,2})/$', 'competition.add_form'),
    (r'^competition/(?P<athlete_id>\w+)/edit/(?P<year>\d{4})/(?P<month>\d{,2})/(?P<day>\d{,2})/(?P<competition_id>\d+)/$', 'competition.edit_form'),
)
