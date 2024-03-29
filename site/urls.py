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
from hollo_settings import PROJECT_DIR

from django.conf.urls.defaults import *
from django.contrib import admin
import athletelog.views

admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', athletelog.views.index),

    # Uncomment this for admin:
    (r'^admin/(.*)', admin.site.root),

    # Log URLs
    (r'^log/', include('athletelog.urls')),

    # Site Media - TODO: Odstranit pri nahrani na server
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.join(PROJECT_DIR, 'media')}),
)
