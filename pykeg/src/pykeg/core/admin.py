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

from django.contrib import admin

from pykeg.core import models
from pykeg.core import util

admin.site.register(models.UserProfile)

admin.site.register(models.KegSize)

class KegbotSiteAdmin(admin.ModelAdmin):
  list_display = ('name', 'is_active')
  list_filter = ('is_active',)
admin.site.register(models.KegbotSite, KegbotSiteAdmin)

class KegTapAdmin(admin.ModelAdmin):
  list_display = ('name', 'meter_name', 'relay_name', 'current_keg')
admin.site.register(models.KegTap, KegTapAdmin)

class KegAdmin(admin.ModelAdmin):
  list_display = ('seqn', 'type')
admin.site.register(models.Keg, KegAdmin)

class DrinkAdmin(admin.ModelAdmin):
  list_display = ('seqn', 'user', 'keg', 'starttime')
  list_filter = ('keg', 'status', 'starttime')
  search_fields = ('seqn', 'user__username')
admin.site.register(models.Drink, DrinkAdmin)

class AuthenticationTokenAdmin(admin.ModelAdmin):
  list_display = ('auth_device', 'user', 'token_value', 'nice_name', 'enabled', 'IsActive')
  list_filter = ('auth_device', 'enabled')
  search_fields = ('user__username', 'token_value', 'nice_name')
admin.site.register(models.AuthenticationToken, AuthenticationTokenAdmin)

class DrinkingSessionAdmin(admin.ModelAdmin):
  list_display = ('id', 'site', 'seqn', 'starttime', 'endtime', 'volume_ml', 'GetTitle')
  list_filter = ('site', 'starttime')
  search_fields = ('name',)
admin.site.register(models.DrinkingSession, DrinkingSessionAdmin)

class ThermoSensorAdmin(admin.ModelAdmin):
  list_display = ('nice_name', 'raw_name')

admin.site.register(models.ThermoSensor, ThermoSensorAdmin)

def thermolog_deg_c(obj):
  return '%.2f C' % (obj.temp,)

def thermolog_deg_f(obj):
  return '%.2f F' % (util.CtoF(obj.temp),)

class ThermologAdmin(admin.ModelAdmin):
  list_display = ('sensor', thermolog_deg_c, thermolog_deg_f, 'time')
  list_filter = ('sensor', 'time')

admin.site.register(models.Thermolog, ThermologAdmin)

class ThermoSummaryLogAdmin(admin.ModelAdmin):
  list_display = ('sensor', 'date', 'min_temp', 'max_temp', 'mean_temp')
  list_filter = ('sensor', 'date')

admin.site.register(models.ThermoSummaryLog, ThermoSummaryLogAdmin)

class SystemEventAdmin(admin.ModelAdmin):
  list_display = ('seqn', 'kind', 'when', 'user', 'drink', 'keg', 'session')
  list_filter = ('kind', 'when')
admin.site.register(models.SystemEvent, SystemEventAdmin)

class PictureAdmin(admin.ModelAdmin):
  list_display = ('seqn', 'created_date', 'user', 'drink', 'keg', 'session', 'caption')
  list_filter = ('created_date',)
admin.site.register(models.Picture, PictureAdmin)

class SiteSettingsAdmin(admin.ModelAdmin):
  list_display = ('site', 'title', 'description')
admin.site.register(models.SiteSettings, SiteSettingsAdmin)
