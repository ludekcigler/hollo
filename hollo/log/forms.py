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

import time

from django import newforms as forms
from django.utils.dates import MONTHS

from hollo.log import models

class ChangeViewForm(forms.Form):
    month = forms.ChoiceField(choices=[(month, MONTHS[month]) for month in xrange(1, 13)], label='Měsíc', initial=time.localtime()[1])
    year = forms.IntegerField(min_value=1900, max_value=2100, label='Rok', initial=time.localtime()[0],
                              widget=forms.TextInput(attrs={'size': '4'}))

class WorkoutChangeViewForm(ChangeViewForm): 
    view_type = forms.ChoiceField(choices=[('weekly', 'Týdenní'), ('monthly', 'Měsíční')], label='Pohled')
    week = forms.IntegerField(min_value=1, max_value=53, label='Týden', widget=forms.TextInput(attrs={'size': '2'}))

class CompetitionChangeViewForm(ChangeViewForm):
    view_type = forms.ChoiceField(choices=[('monthly', 'Měsíční'), ('yearly', 'Roční')], label='Pohled')

class SettingsUserForm(forms.Form):
    first_name = forms.CharField(min_length=1, label='Jméno')
    last_name = forms.CharField(min_length=1, label='Příjmení')
    email = forms.EmailField(label='Email')
    club = forms.CharField(required=False, label='Klub')
    athlete_group = forms.ChoiceField(label='Tréninková skupina', required=False)

class SettingsImageForm(forms.Form):
    image = forms.FileField(label='Obrázek')

class SettingsPasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput, label='Heslo')
    password_retype = forms.CharField(widget=forms.PasswordInput, label='Heslo znovu')

class SettingsAuthRequestForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea, label='Zpráva', required=False)

class CompetitionForm(forms.Form):
    id = forms.CharField(widget=forms.HiddenInput, required=False)
    day = forms.DateField(widget=forms.HiddenInput)
    event = forms.ChoiceField(label='Disciplína')
    event_info = forms.CharField(required=False, label='Podrobnosti')
    result = forms.CharField(label='Výkon', initial='')
    place = forms.CharField(label='Místo', initial='')
    note = forms.CharField(required=False, widget=forms.Textarea, label='Poznámka')

class WorkoutForm(forms.Form):
    day = forms.DateField(widget=forms.HiddenInput)
    id = forms.CharField(widget=forms.HiddenInput, required=False)
    num_workout_items = forms.IntegerField(min_value=0, widget=forms.HiddenInput)
    weather = forms.CharField(label='Počasí', required=False)
    rating_satisfaction = forms.IntegerField(min_value=models.Workout.MIN_RATING, max_value=models.Workout.MAX_RATING, label='Spokojenost')
    rating_difficulty = forms.IntegerField(min_value=models.Workout.MIN_RATING, max_value=models.Workout.MAX_RATING, label='Obtížnost')
    note = forms.CharField(widget=forms.Textarea, required=False, label='Poznámka')

class WorkoutItemForm(forms.Form):
    type = forms.ChoiceField(label='Typ', initial='Roz')
    desc = forms.CharField(label='Popis', min_length=1, initial='')
    num_data = forms.DecimalField(decimal_places=2, label='km/kg', initial=0)
