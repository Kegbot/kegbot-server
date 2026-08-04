"""FilterSets for API list endpoints.

These power the query parameters the frontend uses for drill-down pages
(per-user drink lists, keg detail, session date archives) and search.
"""

import datetime

from django.db.models import Q
from django.utils import timezone
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


def session_date_range(year, month=None, day=None):
    """[start, end) datetimes covering a year/month/day in the site timezone.

    Returns None for out-of-range dates (month 13, February 30, ...).
    """
    tz = timezone.get_current_timezone()
    try:
        if day is not None:
            start = datetime.datetime(year, month, day)
            end = start + datetime.timedelta(days=1)
        elif month is not None:
            start = datetime.datetime(year, month, 1)
            end = (
                datetime.datetime(year + 1, 1, 1)
                if month == 12
                else datetime.datetime(year, month + 1, 1)
            )
        else:
            start = datetime.datetime(year, 1, 1)
            end = datetime.datetime(year + 1, 1, 1)
    except ValueError:
        return None
    return start.replace(tzinfo=tz), end.replace(tzinfo=tz)


class DrinkingSessionFilter(filters.FilterSet):
    # Declared for form parsing and schema generation; applied together
    # in filter_queryset as a datetime range. A range keeps the site
    # timezone conversion in Python: date lookups (start_time__year)
    # compile to CONVERT_TZ on MySQL, which silently returns NULL when
    # the server's timezone tables aren't loaded.
    year = filters.NumberFilter(method="noop")
    month = filters.NumberFilter(method="noop")
    day = filters.NumberFilter(method="noop")

    class Meta:
        model = models.DrinkingSession
        fields = ["year", "month", "day"]

    def noop(self, queryset, name, value):
        return queryset

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        data = self.form.cleaned_data
        year = data.get("year")
        month = data.get("month")
        day = data.get("day")
        if year is None:
            return queryset
        # A day is meaningless without a month; ignore it in that case.
        month = int(month) if month is not None else None
        day = int(day) if day is not None and month is not None else None
        bounds = session_date_range(int(year), month, day)
        if bounds is None:
            return queryset.none()
        start, end = bounds
        return queryset.filter(start_time__gte=start, start_time__lt=end)


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
