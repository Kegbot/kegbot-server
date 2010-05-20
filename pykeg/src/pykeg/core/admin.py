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

admin.site.register(models.UserPicture)
admin.site.register(models.UserLabel)
admin.site.register(models.UserProfile)

admin.site.register(models.KegSize)

class KegTapAdmin(admin.ModelAdmin):
  list_display = ('name', 'meter_name', 'current_keg')
admin.site.register(models.KegTap, KegTapAdmin)

class KegAdmin(admin.ModelAdmin):
  list_display = ('id', 'type')
admin.site.register(models.Keg, KegAdmin)

class DrinkAdmin(admin.ModelAdmin):
  list_display = ('id', 'user', 'keg', 'endtime')
  list_filter = ('keg', 'status', 'endtime')
  search_fields = ('id', 'user__username')
admin.site.register(models.Drink, DrinkAdmin)

class AuthenticationTokenAdmin(admin.ModelAdmin):
  list_display = ('auth_device', 'user', 'token_value', 'enabled', 'IsActive')
  list_filter = ('auth_device', 'enabled')
  search_fields = ('user__username', 'token_value')
admin.site.register(models.AuthenticationToken, AuthenticationTokenAdmin)

admin.site.register(models.BAC)
admin.site.register(models.DrinkingSession)

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

admin.site.register(models.RelayLog)

class ConfigAdmin(admin.ModelAdmin):
  list_display = ('key', 'value')
  search_fields = ('key', 'value')
admin.site.register(models.Config, ConfigAdmin)
