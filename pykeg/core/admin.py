# Copyright 2013 Mike Wakerly <opensource@hoho.com>
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

"""Django admin site settings for core models."""

from django.contrib import admin
from kegbot.util import util
from pykeg.core import models

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
    list_display = ('id', 'type', 'online')
    list_filter = ('online', )
    search_fields = ('id', 'type__name')
admin.site.register(models.Keg, KegAdmin)

class DrinkAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'keg', 'time')
    list_filter = ('keg', 'time')
    search_fields = ('id', 'user__username')
admin.site.register(models.Drink, DrinkAdmin)

class AuthenticationTokenAdmin(admin.ModelAdmin):
    list_display = ('auth_device', 'user', 'token_value', 'nice_name', 'enabled', 'IsActive')
    list_filter = ('auth_device', 'enabled')
    search_fields = ('user__username', 'token_value', 'nice_name')
admin.site.register(models.AuthenticationToken, AuthenticationTokenAdmin)

class DrinkingSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'start_time', 'end_time', 'volume_ml', 'GetTitle')
    list_filter = ('start_time',)
    search_fields = ('name',)
admin.site.register(models.DrinkingSession, DrinkingSessionAdmin)

class ThermoSensorAdmin(admin.ModelAdmin):
    list_display = ('raw_name', 'nice_name')
    search_fields = list_display
admin.site.register(models.ThermoSensor, ThermoSensorAdmin)

def thermolog_deg_c(obj):
    return '%.2f C' % (obj.temp,)

def thermolog_deg_f(obj):
    return '%.2f F' % (util.CtoF(obj.temp),)

class ThermologAdmin(admin.ModelAdmin):
    list_display = ('sensor', thermolog_deg_c, thermolog_deg_f, 'time')
    list_filter = ('sensor', 'time')

admin.site.register(models.Thermolog, ThermologAdmin)

class SystemEventAdmin(admin.ModelAdmin):
    list_display = ('id', 'kind', 'time', 'user', 'drink', 'keg', 'session')
    list_filter = ('kind', 'time')
admin.site.register(models.SystemEvent, SystemEventAdmin)

class PictureAdmin(admin.ModelAdmin):
    list_display = ('id', 'time')
    list_filter = ('time',)
admin.site.register(models.Picture, PictureAdmin)

class PourPictureAdmin(admin.ModelAdmin):
    list_display = ('id', 'time', 'user', 'drink', 'keg', 'session', 'caption')
    list_filter = ('time',)
admin.site.register(models.PourPicture, PourPictureAdmin)

class BeerTypeInline(admin.TabularInline):
    model = models.BeerType
    fieldsets = (
      (None, {
          'fields': ('name', 'brewer', 'style', 'abv', 'image', 'untappd_beer_id')
      }),
    )

class BrewerAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'added', 'edited')
    ordering = ('name',)
    search_fields = ('name',)
    inlines = [
        BeerTypeInline,
    ]
    fieldsets = (
      (None, {
          'fields': ('name', 'country', 'origin_state', 'origin_city', 'image')
      }),
      ('Advanced options', {
          'classes': ('collapse',),
          'fields': ('production', 'url', 'description')
      }),
    )
admin.site.register(models.Brewer, BrewerAdmin)

class BeerStyleAdmin(admin.ModelAdmin):
    list_display = ('name', 'added', 'edited')
    model = models.BeerStyle
    ordering = ('name',)
    search_fields = ('name',)
admin.site.register(models.BeerStyle, BeerStyleAdmin)

class BeerTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'brewer', 'style', 'added', 'edited')
    ordering = ('brewer__name', 'name')
    search_fields = ('name', 'brewer__name')
    fieldsets = (
      (None, {
          'fields': ('name', 'brewer', 'style', 'abv', 'image')
      }),
      ('Advanced options', {
          'classes': ('collapse',),
          'fields': ('calories_oz', 'carbs_oz', 'original_gravity',
              'specific_gravity', 'beerdb_id', 'untappd_beer_id')
      }),
    )

admin.site.register(models.BeerType, BeerTypeAdmin)
