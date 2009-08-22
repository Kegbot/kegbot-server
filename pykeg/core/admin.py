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

admin.site.register(models.UserPicture)
admin.site.register(models.UserLabel)
admin.site.register(models.UserProfile)
admin.site.register(models.Brewer)
admin.site.register(models.BeerStyle)

class BeerTypeAdmin(admin.ModelAdmin):
  list_display = ('name', 'brewer', 'style')
admin.site.register(models.BeerType, BeerTypeAdmin)

admin.site.register(models.KegSize)

class KegAdmin(admin.ModelAdmin):
  list_display = ('id', 'type')
admin.site.register(models.Keg, KegAdmin)

admin.site.register(models.Drink)
admin.site.register(models.Token)
admin.site.register(models.BAC)
admin.site.register(models.UserDrinkingSession)
admin.site.register(models.UserDrinkingSessionAssignment)
admin.site.register(models.DrinkingSessionGroup)
admin.site.register(models.Thermolog)
admin.site.register(models.RelayLog)
admin.site.register(models.Config)
