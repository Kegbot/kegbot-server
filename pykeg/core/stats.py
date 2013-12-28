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

"""Methods to generate cached statistics from drinks."""

import copy
import inspect
import itertools
import logging

from django.db import transaction

from pykeg.core import models
from kegbot.util import util

STAT_MAP = {}

def stat(statname):
    def decorate(f):
        setattr(f, 'statname', statname)
        return f
    return decorate

class StatsBuilder:
    def __init__(self, drink, drink_qs, previous=None):
        self.drink = drink
        self.drinks = drink_qs
        self.previous = util.AttrDict(copy.deepcopy(previous))
        self.STAT_MAP = {}
        for name, fn in inspect.getmembers(self, inspect.ismethod):
            if hasattr(fn, 'statname'):
                self.STAT_MAP[fn.statname] = fn

    def build(self, tag=None):
        stats = util.AttrDict()
        if not self.drink:
            return stats
        if self.previous:
            stats = copy.deepcopy(self.previous)
        for statname, fn in self.STAT_MAP.iteritems():
            previous = self.previous.get(statname, None)
            val = fn(previous)
            if val is None:
                raise ValueError('Stat generator for %s returned None' % statname)
            stats[statname] = val
        return stats

    @stat('last_drink_id')
    def LastDrinkId(self, previous):
        return self.drink.id

    @stat('total_volume_ml')
    def TotalVolume(self, previous):
        if not previous:
            return sum(drink.volume_ml for drink in self.drinks)
        else:
            return previous + self.drink.volume_ml

    @stat('total_pours')
    def TotalPours(self, previous):
        if not previous:
            return self.drinks.count()
        else:
            return previous + 1

    @stat('average_volume_ml')
    def AverageVolume(self, previous):
        if not previous:
            count = self.drinks.count()
            average = 0.0
            if count:
                average = sum(drink.volume_ml for drink in self.drinks) / float(count)
            return average
        else:
            vol = self.previous.total_volume_ml
            count = self.previous.total_pours
            vol += self.drink.volume_ml
            count += 1
            return vol / float(count)

    @stat('greatest_volume_ml')
    def GreatestVolume(self, previous):
        if not previous:
            res = 0
            drinks = self.drinks.order_by('-volume_ml')
            if drinks.count():
                res = drinks[0].volume_ml
            return float(res)
        else:
            return float(max(self.drink.volume_ml, previous))

    @stat('greatest_volume_id')
    def GreatestVolumeId(self, previous):
        if not previous:
            res = 0
            drinks = self.drinks.order_by('-volume_ml')
            if drinks.count():
                res = drinks[0].id
            return res
        else:
            if self.drink.volume_ml > self.previous.greatest_volume_ml:
                return self.drink.id
            return previous

    @stat('volume_by_day_of_week')
    def VolumeByDayOfweek(self, previous):
        if not previous:
            # Note: uses the session's start_time, rather than the drink's. This
            # causes late-night sessions to be reported for the day on which they were
            # started.
            volmap = {}
            for drink in self.drinks:
                weekday = str(drink.session.start_time.strftime('%w'))
                if weekday not in volmap:
                    volmap[weekday] = 0.0
                volmap[weekday] += drink.volume_ml
            return volmap
        else:
            drink_weekday = str(self.drink.session.start_time.strftime('%w'))
            previous[drink_weekday] = previous.get(drink_weekday, 0) + self.drink.volume_ml
            return previous

    @stat('registered_drinkers')
    def RegisteredDrinkers(self, previous):
        if previous is None:
            drinkers = set()
            for drink in self.drinks:
                if drink.user:
                    drinkers.add(str(drink.user.username))
            return list(drinkers)
        else:
            if self.drink.user:
                username = str(self.drink.user.username)
                if username not in previous:
                    previous.append(str(username))
            return previous

    @stat('sessions_count')
    def SessionsCount(self, previous):
        if not previous:
            all_sessions = set()
            for drink in self.drinks:
                all_sessions.add(drink.session.id)
            return len(all_sessions)
        else:
            first_drink = self.drink.session.drinks.order_by('id')[0]
            if self.drink.id == first_drink.id:
                previous += 1
            return previous

    @stat('volume_by_year')
    def VolumeByYear(self, previous):
        if not previous:
            ret = {}
            for drink in self.drinks:
                year = str(drink.time.year)
                ret[year] = ret.get(year, 0) + drink.volume_ml
            return ret
        else:
            year = str(self.drink.time.year)
            previous[year] = previous.get(year, 0) + self.drink.volume_ml
            return previous

    @stat('has_guest_pour')
    def HasGuestPour(self, previous):
        if not previous:
            return self.drinks.filter(user_id=None).count() > 0
        else:
            return bool(previous or self.drink.user is None)

    @stat('volume_by_drinker')
    def VolumeByDrinker(self, previous):
        if not previous:
            volmap = {}
            for drink in self.drinks:
                if drink.user:
                    u = str(drink.user.username)
                else:
                    u = ''
                volmap[u] = float(volmap.get(u, 0) + drink.volume_ml)
            return volmap
        else:
            if self.drink.user:
                u = str(self.drink.user.username)
            else:
                u = ''
            orig = previous.get(u, 0)
            previous[u] = float(orig + self.drink.volume_ml)
            return previous


def invalidate(drink):
    """Clears all statistics.

    Args:
        drink: The starting point to invalidate; all stats starting from this
            drink will be deleted.  If None, deletes *all* stats.
    """
    with transaction.atomic():
        if drink:
            models.SystemStats.objects.filter(drink_id__gte=drink.id).delete()
            models.KegStats.objects.filter(drink_id__gte=drink.id).delete()
            models.UserStats.objects.filter(drink_id__gte=drink.id).delete()
            models.SessionStats.objects.filter(drink_id__gte=drink.id).delete()
        else:
            models.SystemStats.objects.all().delete()
            models.KegStats.objects.all().delete()
            models.UserStats.objects.all().delete()
            models.SessionStats.objects.all().delete()

def _get_previous(drink, qs):
    qs = qs.filter(drink_id__lt=drink.id).order_by('-id')[:1]
    if qs.count():
        return qs[0].stats
    return {}

def build_system_stats(drink):
    """Builds (but does not save) system stats dictionary for drink."""
    qs = models.Drink.objects.filter(id__lte=drink.id)
    previous = _get_previous(drink, models.SystemStats.objects.all())
    builder = StatsBuilder(drink, qs, previous)
    return builder.build('system')

def generate_system_stats(drink):
    """Builds and saves system stats record for drink."""
    stats = build_system_stats(drink)
    return models.SystemStats.objects.create(drink=drink, stats=stats)

def build_keg_stats(drink):
    """Builds (but does not save) keg stats dictionary for drink."""
    if drink.keg:
        qs = models.Drink.objects.filter(id__lte=drink.id, keg_id=drink.keg.id)
        previous = _get_previous(drink,
            models.KegStats.objects.filter(keg=drink.keg))
        builder = StatsBuilder(drink, qs, previous)
        return builder.build('keg ' + str(drink.keg.id))

def generate_keg_stats(drink):
    """Builds and saves keg stats record for drink."""
    stats = build_keg_stats(drink)
    if stats:
        return models.KegStats.objects.create(drink=drink, keg=drink.keg, stats=stats)

def build_user_stats(drink):
    """Builds (but does not save) user stats dictionary for drink."""
    if drink.user:
        user_id = drink.user.id
    else:
        user_id = None
    qs = models.Drink.objects.filter(id__lte=drink.id, user_id=user_id)
    previous = _get_previous(drink,
        models.UserStats.objects.filter(user=drink.user))
    builder = StatsBuilder(drink, qs, previous)
    return builder.build('user ' + str(user_id))

def generate_user_stats(drink):
    """Builds and saves user stats record for drink."""
    stats = build_user_stats(drink)
    return models.UserStats.objects.create(drink=drink, user=drink.user, stats=stats)

def build_session_stats(drink):
    """Builds (but does not save) session stats dictionary for drink."""
    if drink.session:
        qs = models.Drink.objects.filter(id__lte=drink.id, session_id=drink.session.id)
        previous = _get_previous(drink,
            models.SessionStats.objects.filter(session=drink.session))
        builder = StatsBuilder(drink, qs, previous)
        return builder.build('session ' + str(drink.session.id))

def generate_session_stats(drink):
    """Builds and saves session stats record for drink."""
    stats = build_session_stats(drink)
    if stats:
        return models.SessionStats.objects.create(drink=drink,
            session=drink.session, stats=stats)

def generate(drink, invalidate_first=True):
    """Generate all stats for this drink.

    Args:
        drink: The drink.
        invalidate_first: If True, deletes any existing records for (or after)
            this drink first.
    """
    with transaction.atomic():
        if invalidate_first:
            invalidate(drink)

        generate_system_stats(drink)
        generate_keg_stats(drink)
        generate_user_stats(drink)
        generate_session_stats(drink)

if __name__ == '__main__':
    import cProfile
    command = """main()"""
    cProfile.runctx( command, globals(), locals(), filename="stats.profile" )
