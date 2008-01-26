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

import athletelog
import athletelog.views
import athletelog.views.competition
import athletelog.views.workout
import athletelog.views.user
import athletelog.views.settings

urlpatterns = patterns('athletelog.views',
    (r'^$', athletelog.views.index),
    (r'^login/$', athletelog.views.user.login),
    (r'^logout/$', athletelog.views.user.logout),
    (r'^auth/$', athletelog.views.user.auth),

    (r'^error/(?P<error_code>\d+)/$', athletelog.views.error),

    (r'^change_athlete/(?P<view_type>workout|competition)/$', athletelog.views.change_athlete),

    # Settings views
    (r'^settings/$', athletelog.views.settings.index),
    (r'^settings/user/$', athletelog.views.settings.user),
    (r'^settings/user/change_password/$', athletelog.views.settings.user_change_password),
    (r'^settings/user/remove_image/$', athletelog.views.settings.user_remove_image),
    (r'^settings/user/edit_image/$', athletelog.views.settings.user_edit_image),
    (r'^settings/user/upload_image/$', athletelog.views.settings.user_upload_image),
    (r'^settings/my_athletes/$', athletelog.views.settings.my_athletes),
    (r'^settings/friends/$', athletelog.views.settings.friends),
    (r'^settings/friends/add/$', athletelog.views.settings.friends_add),
    (r'^settings/friends/add/(?P<athlete_id>\w+)/$', athletelog.views.settings.friends_add_edit_message),
    (r'^settings/friends/add_submit/(?P<athlete_id>\w+)/$', athletelog.views.settings.friends_add_submit),
    (r'^settings/friends/remove/(?P<athlete_id>\w+)/$', athletelog.views.settings.friends_remove),
    (r'^settings/friends/block/(?P<person_id>\w+)/$', athletelog.views.settings.friends_block),
    (r'^settings/friends/unblock/(?P<person_id>\w+)/$', athletelog.views.settings.friends_unblock),
    (r'^settings/friends/auth/(?P<person_id>\w+)/$', athletelog.views.settings.friends_auth),
    (r'^settings/friends/auth_reject/(?P<person_id>\w+)/$', athletelog.views.settings.friends_auth_reject),
    (r'^settings/friends/auth_cancel/(?P<person_id>\w+)/$', athletelog.views.settings.friends_auth_cancel),
    (r'^settings/friends/auth_list/$', athletelog.views.settings.friends_auth_list),

    # Workout
    (r'workout/(?P<athlete_id>\w+)/$', athletelog.views.workout.index),

    (r'^workout/(?P<athlete_id>\w+)/week/(?P<year>\d{4})/(?P<week>\d{,2})/$', athletelog.views.workout.weekly_view),
    (r'^workout/(?P<athlete_id>\w+)/week/(?P<year>\d{4})/(?P<week>\d{,2})/day/(?P<detail_year>\d{4})/(?P<detail_month>\d{,2})/(?P<detail_day>\d{,2})/$', 
        athletelog.views.workout.weekly_view_detail),
    (r'^workout/(?P<athlete_id>\w+)/month/(?P<year>\d{4})/(?P<month>\d{,2})/$', athletelog.views.workout.monthly_view),
    (r'^workout/(?P<athlete_id>\w+)/month/(?P<year>\d{4})/(?P<month>\d{,2})/(?P<detail_day>\d{,2})/$', athletelog.views.workout.monthly_view_detail),

    (r'^workout/(?P<athlete_id>\w+)/add_submit/$', athletelog.views.workout.add_submit),
    (r'^workout/(?P<athlete_id>\w+)/edit_submit/$', athletelog.views.workout.edit_submit),
    (r'^workout/(?P<athlete_id>\w+)/remove/(?P<workout_id>\d+)/$', athletelog.views.workout.remove_workout),
    (r'^workout/(?P<athlete_id>\w+)/add/(?P<year>\d{4})/(?P<month>\d{,2})/(?P<day>\d{,2})/$', athletelog.views.workout.add_form),
    (r'^workout/(?P<athlete_id>\w+)/edit/(?P<year>\d{4})/(?P<month>\d{,2})/(?P<day>\d{,2})/(?P<workout_id>\d+)/$', athletelog.views.workout.edit_form),

    (r'^workout/(?P<athlete_id>\w+)/change_view/$', athletelog.views.workout.change_view),

    # Competition
    (r'^competition/(?P<athlete_id>\w+)/$', athletelog.views.competition.index),
    (r'^competition/(?P<athlete_id>\w+)/add_submit/$', athletelog.views.competition.add_submit),
    (r'^competition/(?P<athlete_id>\w+)/edit_submit/$', athletelog.views.competition.edit_submit),

    (r'^competition/(?P<athlete_id>\w+)/remove/(?P<competition_id>\d+)/$', athletelog.views.competition.remove_competition),

    (r'^competition/(?P<athlete_id>\w+)/month/(?P<year>\d{4})/(?P<month>\d{,2})/$', athletelog.views.competition.monthly_view),
    (r'^competition/(?P<athlete_id>\w+)/month/(?P<year>\d{4})/(?P<month>\d{,2})/(?P<competition_id>\d+)/$',
        athletelog.views.competition.monthly_view),

    (r'^competition/(?P<athlete_id>\w+)/year/(?P<year>\d{4})/$', athletelog.views.competition.yearly_view),
    (r'^competition/(?P<athlete_id>\w+)/year/(?P<year>\d{4})/(?P<competition_id>\d+)/$', 
        athletelog.views.competition.yearly_view),

    (r'^competition/(?P<athlete_id>\w+)/change_view/$', athletelog.views.competition.change_view),

    (r'^competition/(?P<athlete_id>\w+)/add/(?P<year>\d{4})/(?P<month>\d{,2})/(?P<day>\d{,2})/$', athletelog.views.competition.add_form),
    (r'^competition/(?P<athlete_id>\w+)/edit/(?P<year>\d{4})/(?P<month>\d{,2})/(?P<day>\d{,2})/(?P<competition_id>\d+)/$', athletelog.views.competition.edit_form),

    # Hijax webpage snippets
    (r'^snippets/workout/(?P<athlete_id>\w+)/day/(?P<year>\d{4})/(?P<month>\d{,2})/(?P<day>\d{,2})/$', athletelog.views.workout.daily_summary_snippet),
    (r'^snippets/workout/(?P<athlete_id>\w+)/weekly_summary/(?P<year>\d{4})/(?P<week>\d{,2})/$', athletelog.views.workout.weekly_summary_snippet),
    (r'^snippets/workout/(?P<athlete_id>\w+)/monthly_summary/(?P<year>\d{4})/(?P<month>\d{,2})/$', athletelog.views.workout.monthly_summary_snippet),

    (r'^snippets/workout/(?P<athlete_id>\w+)/add/(?P<year>\d{4})/(?P<month>\d{,2})/(?P<day>\d{,2})/$', athletelog.views.workout.add_form_snippet),
    (r'^snippets/workout/(?P<athlete_id>\w+)/edit/(?P<year>\d{4})/(?P<month>\d{,2})/(?P<day>\d{,2})/(?P<workout_id>\d+)/$', athletelog.views.workout.edit_form_snippet),
    (r'^snippets/workout/(?P<athlete_id>\w+)/week/(?P<year>\d{4})/(?P<week>\d{,2})/$', athletelog.views.workout.weekly_view_snippet),
    (r'^snippets/workout/(?P<athlete_id>\w+)/month/(?P<year>\d{4})/(?P<month>\d{,2})/$', athletelog.views.workout.monthly_view_snippet),

    (r'^snippets/competition/(?P<athlete_id>\w+)/add/(?P<year>\d{4})/(?P<month>\d{,2})/(?P<day>\d{,2})/$', athletelog.views.competition.add_form_snippet),
    (r'^snippets/competition/(?P<athlete_id>\w+)/edit/(?P<year>\d{4})/(?P<month>\d{,2})/(?P<day>\d{,2})/(?P<competition_id>\d+)/$', athletelog.views.competition.edit_form_snippet),
    (r'^snippets/competition/(?P<athlete_id>\w+)/total_summary/$', athletelog.views.competition.total_summary_snippet),
    (r'^snippets/competition/(?P<athlete_id>\w+)/yearly_summary/(?P<year>\d{4})/$', athletelog.views.competition.yearly_summary_snippet),
    (r'^snippets/competition/(?P<athlete_id>\w+)/monthly_summary/(?P<year>\d{4})/(?P<month>\d{,2})/$', athletelog.views.competition.monthly_summary_snippet),

    # Javascript-generating views
    (r'^js/event_info/', athletelog.views.js_event_info),
    (r'^js/workout_type_info/', athletelog.views.js_workout_type_info),
    #(r'^js/', athletelog.views.js_engine_experimental),

    # REST JSON API
    #(r'^api/workout/(?P<athlete_id>\w+)/week/(?P<year>\d{4})/(?P<week>\d{,2})/$', athletelog.views.workout.api_weekly_view),
    #(r'^api/workout/(?P<athlete_id>\w+)/month/(?P<year>\d{4})/(?P<month>\d{,2})/$', athletelog.views.workout.api_monthly_view),
    (r'^api/workout/(?P<athlete_id>\w+)/add/$', athletelog.views.workout.api_add_workout),
    (r'^api/workout/(?P<athlete_id>\w+)/edit/$', athletelog.views.workout.api_edit_workout),
    (r'^api/competition/(?P<athlete_id>\w+)/add/$', athletelog.views.competition.api_add_competition),
    (r'^api/competition/(?P<athlete_id>\w+)/edit/$', athletelog.views.competition.api_edit_competition),

)
