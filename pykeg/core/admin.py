"""Django admin site settings for core models."""

from django.contrib import admin

from pykeg.core import models
from pykeg.core.util import CtoF


class UserAdmin(admin.ModelAdmin):
    list_display = (
        "username",
        "email",
        "date_joined",
        "last_login",
        "is_active",
        "is_superuser",
        "is_staff",
    )
    list_filter = ("is_active", "is_superuser", "is_staff")


admin.site.register(models.User, UserAdmin)


class KegbotSiteAdmin(admin.ModelAdmin):
    list_display = ("name",)


admin.site.register(models.KegbotSite, KegbotSiteAdmin)


class KegTapAdmin(admin.ModelAdmin):
    list_display = ("name", "current_keg", "sort_order")


admin.site.register(models.KegTap, KegTapAdmin)


class KegAdmin(admin.ModelAdmin):
    list_display = ("id", "type")
    list_filter = ("status",)
    search_fields = ("id", "type__name")


admin.site.register(models.Keg, KegAdmin)


class DrinkAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "keg", "time")
    list_filter = ("keg", "time")
    search_fields = ("id", "user__username")


admin.site.register(models.Drink, DrinkAdmin)


class AuthenticationTokenAdmin(admin.ModelAdmin):
    list_display = ("auth_device", "user", "token_value", "nice_name", "enabled", "IsActive")
    list_filter = ("auth_device", "enabled")
    search_fields = ("user__username", "token_value", "nice_name")


admin.site.register(models.AuthenticationToken, AuthenticationTokenAdmin)


class DrinkingSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "start_time", "end_time", "volume_ml", "GetTitle")
    list_filter = ("start_time",)
    search_fields = ("name",)


admin.site.register(models.DrinkingSession, DrinkingSessionAdmin)


class ThermoSensorAdmin(admin.ModelAdmin):
    list_display = ("raw_name", "nice_name")
    search_fields = list_display


admin.site.register(models.ThermoSensor, ThermoSensorAdmin)


def thermolog_deg_c(obj):
    return "%.2f C" % (obj.temp,)


def thermolog_deg_f(obj):
    return "%.2f F" % (CtoF(obj.temp),)


class ThermologAdmin(admin.ModelAdmin):
    list_display = ("sensor", thermolog_deg_c, thermolog_deg_f, "time")
    list_filter = ("sensor", "time")


admin.site.register(models.Thermolog, ThermologAdmin)


class SystemEventAdmin(admin.ModelAdmin):
    list_display = ("id", "kind", "time", "user", "drink", "keg", "session")
    list_filter = ("kind", "time")


admin.site.register(models.SystemEvent, SystemEventAdmin)


class PictureAdmin(admin.ModelAdmin):
    list_display = ("id", "time", "user", "keg", "session", "caption")
    list_filter = ("time",)


admin.site.register(models.Picture, PictureAdmin)

admin.site.register(models.Beverage)
admin.site.register(models.BeverageProducer)

admin.site.register(models.Controller)
admin.site.register(models.FlowMeter)
admin.site.register(models.FlowToggle)
