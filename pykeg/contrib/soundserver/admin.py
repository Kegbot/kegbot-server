# Copyright 2010 Mike Wakerly <opensource@hoho.com>
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

from django.contrib import admin

from pykeg.contrib.soundserver import models

class SoundFileAdmin(admin.ModelAdmin):
  list_display = ('title', 'sound', 'active')
admin.site.register(models.SoundFile, SoundFileAdmin)

class SoundEventAdmin(admin.ModelAdmin):
  list_display = ('event_name', 'event_predicate', 'SoundTitle')
  list_filter = ('event_name',)
  search_fileds = ('event_name', 'SoundTitle')
admin.site.register(models.SoundEvent, SoundEventAdmin)
