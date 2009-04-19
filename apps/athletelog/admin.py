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

from django.contrib import admin
from athletelog.models import Person, Athlete, Coach, AthleteGroup, AuthorizationRequest, TrackEvent, Competition, Workout, WorkoutType, WorkoutItem 


class PersonAdmin(admin.ModelAdmin):
    list_display = ('user',)

admin.site.register(Person, PersonAdmin)

class AthleteAdmin(admin.ModelAdmin):
    pass

admin.site.register(Athlete, AthleteAdmin)

class CoachAdmin(admin.ModelAdmin):
    pass

admin.site.register(Coach, CoachAdmin)

class AthleteGroupAdmin(admin.ModelAdmin):
    pass

admin.site.register(AthleteGroup, AthleteGroupAdmin)

class AuthorizationRequestAdmin(admin.ModelAdmin):
    pass

admin.site.register(AuthorizationRequest, AuthorizationRequestAdmin)

class TrackEventAdmin(admin.ModelAdmin):
    list_display = ('name', 'result_type')

admin.site.register(TrackEvent, TrackEventAdmin)

class CompetitionAdmin(admin.ModelAdmin):
    pass

admin.site.register(Competition, CompetitionAdmin)

class WorkoutAdmin(admin.ModelAdmin):
    list_display = ('day', 'athlete', 'weather')

admin.site.register(Workout, WorkoutAdmin)

class WorkoutTypeAdmin(admin.ModelAdmin):
    pass

admin.site.register(WorkoutType, WorkoutTypeAdmin)

class WorkoutItemAdmin(admin.ModelAdmin):
    pass

admin.site.register(WorkoutItem, WorkoutItemAdmin)
