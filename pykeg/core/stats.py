# Copyright 2014 Bevbot LLC, All Rights Reserved
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
import logging

from pykeg.core import models
from kegbot.util import util

STAT_MAP = {}

logger = logging.getLogger(__name__)


class StatsView:
    def __init__(self, user=None, session=None, keg=None):
        self.user = user
        self.session = session
        self.keg = keg

    def __str__(self):
        ret = 'view: '
        if not self.user and not self.keg and not self.session:
            ret += 'system'
        if self.user:
            ret += 'user={} '.format(self.user.username)
        if self.session:
            ret += 'session={} '.format(self.session.id)
        if self.keg:
            ret += 'keg={}'.format(self.keg.id)
        return ret

    def as_tuple(self):
        return (
            self.user.id if self.user else None,
            self.session.id if self.session else None,
            self.keg.id if self.keg else None
        )

    def get_prior_drinks(self, drink):
        """Returns the queryset of prior drinks occurring in this view.

        The result can be empty, which implies the drink is the first drink
        for the given {user, session, keg}.
        """
        qs = models.Drink.objects.filter(id__lt=drink.id)
        if self.user:
            qs = qs.filter(user=self.user.id)
        if self.session:
            qs = qs.filter(session=self.session.id)
        if self.keg:
            qs = qs.filter(keg=self.keg.id)
        return qs.order_by('-id')


class StatsBuilder:
    """Derives statistics from drinks."""

    def __init__(self):
        self.functions = []
        for name, fn in inspect.getmembers(self, inspect.ismethod):
            if not name.startswith('_') and name != 'build':
                self.functions.append((name, fn))

    def build(self, drink, previous_stats):
        if previous_stats is None:
            previous_stats = util.AttrDict()

        logger.debug('build: drink={}'.format(drink.id))
        stats = util.AttrDict()

        for statname, fn in self.functions:
            previous_value = previous_stats.get(statname, None)
            if previous_value is not None:
                val = fn(drink, previous_stats, previous_value=previous_value)
            else:
                val = fn(drink, previous_stats)

            if val is None:
                raise ValueError('Stat generator for %s returned None' % statname)
            stats[statname] = val
        return stats

    def last_drink_id(self, drink, previous_stats, previous_value=0):
        return drink.id

    def keg_ids(self, drink, previous_stats, previous_value=[]):
        ret = copy.copy(previous_value)
        if drink.keg.id not in ret:
            ret.append(drink.keg.id)
        return ret

    def total_volume_ml(self, drink, previous_stats, previous_value=0):
        return previous_value + drink.volume_ml

    def total_pours(self, drink, previous_stats, previous_value=0):
        return previous_value + 1

    def average_volume_ml(self, drink, previous_stats, previous_value=0):
        vol = previous_stats.get('total_volume_ml', 0)
        count = previous_stats.get('total_pours', 0)
        vol += drink.volume_ml
        count += 1
        return vol / float(count)

    def greatest_volume_ml(self, drink, previous_stats, previous_value=0):
        return float(max(drink.volume_ml, previous_value))

    def greatest_volume_id(self, drink, previous_stats, previous_value=0):
        if drink.volume_ml > previous_stats.get('greatest_volume_ml', 0):
            return drink.id
        return previous_value

    def volume_by_day_of_week(self, drink, previous_stats, previous_value={}):
        ret = copy.copy(previous_value)
        drink_weekday = str(drink.session.start_time.strftime('%w'))
        ret[drink_weekday] = ret.get(drink_weekday, 0) + drink.volume_ml
        return ret

    def registered_drinkers(self, drink, previous_stats, previous_value=[]):
        ret = copy.copy(previous_value)
        if drink.user:
            user_id = str(drink.user.id)
            if user_id not in ret:
                ret.append(user_id)
        return ret

    def sessions_count(self, drink, previous_stats, previous_value=0):
        # Use volume_by_session, ensuring our session is captured
        # by injecting a dummy value.
        prev_sessions = previous_stats.get('volume_by_session', {})
        ret = len(prev_sessions.keys())
        if str(drink.session.id) not in prev_sessions:
            ret += 1
        return ret

    def volume_by_year(self, drink, previous_stats, previous_value={}):
        ret = copy.copy(previous_value)
        year = str(drink.time.year)
        ret[year] = ret.get(year, 0) + drink.volume_ml
        return ret

    def has_guest_pour(self, drink, previous_stats, previous_value=False):
        if previous_value:
            return True
        return drink.is_guest_pour()

    def volume_by_drinker(self, drink, previous_stats, previous_value={}):
        ret = copy.copy(previous_value)
        user_id = str(drink.user.id)
        orig = ret.get(user_id, 0)
        ret[user_id] = float(orig + drink.volume_ml)
        return ret

    def volume_by_session(self, drink, previous_stats, previous_value={}):
        ret = copy.copy(previous_value)
        session_id = str(drink.session.id)
        ret[session_id] = ret.get(session_id, 0) + drink.volume_ml
        return ret

    def largest_session(self, drink, previous_stats, previous_value={}):
        if drink.session.volume_ml >= previous_value.get('volume_ml', 0):
            return {
                'session_id': drink.session.id,
                'volume_ml': drink.session.volume_ml,
            }
        return previous_value

BUILDER = StatsBuilder()

### Public methods


def invalidate(drink_id):
    """Clears all statistics starting from (and including) drink_id."""
    logger.debug('--- Invalidating stats since id {}'.format(drink_id))
    models.Stats.objects.filter(drink_id__gte=drink_id).delete()


def invalidate_all():
    logger.debug('--- Invalidating ALL stats')
    models.Stats.objects.all().delete()


def build_for_id(drink_id):
    """Build stats up to and including this drink id, *without*
    considering any subsequent drinks.
    """
    try:
        drink = models.Drink.objects.get(pk=drink_id)
    except models.Drink.DoesNotExist:
        logger.warning('No drink exists with id={}'.format(drink_id))
        return
    _build_all_views(drink)


def rebuild_from_id(drink_id, cb=None):
    """Builds statistics stating from `drink_id`.  Unlike `build_for_id()`,
    this method computes statistics for any subsequent drinks found in the
    database.
    """
    invalidate(drink_id)
    results_cache = {}
    for drink in models.Drink.objects.filter(id__gte=drink_id).order_by('id'):
        _build_all_views(drink, results_cache=results_cache)
        if cb:
            cb(results_cache)


def _build_single_view(drink, view, prior_stats=None):
    """Generates all stats for a drink in the specified view.

    Args:
        drink: The target drink.
        view: The view.
        prior_stats: Dictionary of previous stats for this view.  If None,
            indicates that the prior stats are unknown.  When prior stats
            are unknown, they will be queried or generated as needed.
    """
    logger.debug('>>> Building stats for {}'.format(view))

    build_list = [drink]
    if prior_stats is None:
        prior_stats = util.AttrDict()
        prior_drinks_in_view = view.get_prior_drinks(drink)
        if prior_drinks_in_view.count():
            # Starting with the most recent prior drink, get its stats row.
            # If stats don't exist, add drink to build list and continue
            # until a stats row is found or all drinks are exhausted.
            # N.B. we avoid a recursive algorithm due to potentially large recursion
            # depth in certain cases.
            for prior_drink in prior_drinks_in_view:
                try:
                    prior_stats = util.AttrDict(
                        models.Stats.objects.get(drink=prior_drink, user=view.user,
                            session=view.session, keg=view.keg).stats
                    )
                    break
                except models.Stats.DoesNotExist:
                    build_list.insert(0, prior_drink)

    # Build all drinks on the hit list.
    for build_drink in build_list:
        logger.debug('  - operating on drink {}'.format(build_drink.id))
        stats = BUILDER.build(drink=build_drink, previous_stats=prior_stats)
        models.Stats.objects.create(drink=build_drink, user=view.user,
            session=view.session, keg=view.keg, stats=stats, is_first=(not prior_stats))
        prior_stats = stats
    logger.debug('<<< Done.')
    return stats


def _build_all_views(drink, results_cache=None):
    """Generates all stats "views" based on `drink`.

    Args:
        drink: The target drink.
        invalidate_first: If True, all statistics starting for and following
            this drink will be deleted first.  Typically this is True when the
            target drink was modified, and False when it is a new (newest) Drink.
        results_cache: A cache mapping view.as_tuple() -> stats.  Will be modified
            with the results of this method.
    """
    if results_cache is None:
        results_cache = {}

    for user in (None, drink.user):
        for session in (None, drink.session):
            for keg in (None, drink.keg):
                view = StatsView(user, session, keg)
                cache_key = view.as_tuple()

                prior_stats = results_cache.get(cache_key)
                stats = _build_single_view(drink, view, prior_stats=prior_stats)
                results_cache[cache_key] = stats
