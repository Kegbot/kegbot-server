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

class BeerTypeInline(admin.TabularInline):
  model = models.BeerType

class BrewerAdmin(admin.ModelAdmin):
  inlines = [
    BeerTypeInline,
  ]

admin.site.register(models.Brewer, BrewerAdmin)
admin.site.register(models.BeerStyle)

class BeerTypeAdmin(admin.ModelAdmin):
  list_display = ('name', 'brewer', 'style')
admin.site.register(models.BeerType, BeerTypeAdmin)

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
admin.site.register(models.UserDrinkingSession)
admin.site.register(models.UserDrinkingSessionAssignment)
admin.site.register(models.DrinkingSessionGroup)

def thermolog_deg_c(obj):
  return '%.2f C' % (obj.temp,)

def thermolog_deg_f(obj):
  return '%.2f F' % (util.CtoF(obj.temp),)

class ThermologAdmin(admin.ModelAdmin):
  list_display = ('name', thermolog_deg_c, thermolog_deg_f, 'time')
  list_filter = ('name', 'time')

admin.site.register(models.Thermolog, ThermologAdmin)
admin.site.register(models.RelayLog)

class ConfigAdmin(admin.ModelAdmin):
  list_display = ('key', 'value')
  search_fields = ('key', 'value')
admin.site.register(models.Config, ConfigAdmin)
