"""FilterSets for API list endpoints.

These power the query parameters the frontend uses for drill-down pages
(per-user drink lists, keg detail, session date archives) and search.
"""

from django.db.models import Q
from django_filters import rest_framework as filters

from pykeg.core import models


class DrinkFilter(filters.FilterSet):
    username = filters.CharFilter(field_name="user__username")

    class Meta:
        model = models.Drink
        fields = ["user", "keg", "session", "username"]


class KegFilter(filters.FilterSet):
    class Meta:
        model = models.Keg
        fields = ["status"]


class DrinkingSessionFilter(filters.FilterSet):
    year = filters.NumberFilter(field_name="start_time", lookup_expr="year")
    month = filters.NumberFilter(field_name="start_time", lookup_expr="month")
    day = filters.NumberFilter(field_name="start_time", lookup_expr="day")

    class Meta:
        model = models.DrinkingSession
        fields = ["year", "month", "day"]


class SystemEventFilter(filters.FilterSet):
    since = filters.NumberFilter(field_name="id", lookup_expr="gt")
    username = filters.CharFilter(field_name="user__username")

    class Meta:
        model = models.SystemEvent
        fields = ["since", "kind", "user", "username", "keg", "session"]


class ThermologFilter(filters.FilterSet):
    since = filters.IsoDateTimeFilter(field_name="time", lookup_expr="gte")
    until = filters.IsoDateTimeFilter(field_name="time", lookup_expr="lt")

    class Meta:
        model = models.Thermolog
        fields = ["sensor", "since", "until"]


class UserFilter(filters.FilterSet):
    search = filters.CharFilter(method="filter_search")

    class Meta:
        model = models.User
        fields = ["is_active", "is_staff", "search"]

    def filter_search(self, queryset, name, value):
        return queryset.filter(Q(username__icontains=value) | Q(display_name__icontains=value))


class AuthenticationTokenFilter(filters.FilterSet):
    search = filters.CharFilter(method="filter_search")

    class Meta:
        model = models.AuthenticationToken
        fields = ["auth_device", "enabled", "user", "search"]

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(token_value__icontains=value)
            | Q(nice_name__icontains=value)
            | Q(user__username__icontains=value)
        )
