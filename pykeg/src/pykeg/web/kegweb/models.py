# -*- coding: latin-1 -*-
# Copyright 2009 Mike Wakerly <opensource@hoho.com>
#
# This file is part of the Pykeg package of the Kegbot project.
# For more information on Pykeg or Kegbot, see http://kegbot.org/
#
# Pykeg is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# Pykeg is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pykeg.  If not, see <http://www.gnu.org/licenses/>.

from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin

class Page(models.Model):
  STATUS_CHOICES = (
    ('published', 'published'),
    ('draft', 'draft'),
    ('deleted', 'deleted'),
  )
  MARKUP_CHOICES = (
    ('html', 'html'),
    ('markdown', 'markdown'),
    ('plaintext', 'plaintext'),
  )
  name = models.CharField(max_length=256)
  title = models.CharField(max_length=256)
  author = models.ForeignKey(User)
  content = models.TextField()
  status = models.CharField(max_length=32, choices=STATUS_CHOICES,
    default='published')
  markup = models.CharField(max_length=32, choices=MARKUP_CHOICES,
    default='markdown')
  created_on = models.DateTimeField(editable=False, auto_now_add=True)
  last_modified = models.DateTimeField(auto_now=True)

admin.site.register(Page)
