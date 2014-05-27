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
    generate(drink, invalidate_first=False)


def rebuild_from_id(drink_id):
    """Builds statistics stating from `drink_id`.  Unlike `build_for_id()`,
    this method computes statistics for any subsequent drinks found in the
    database.
    """
    invalidate(drink_id)
    for drink in models.Drink.objects.filter(id__gte=drink_id).order_by('id'):
        generate(drink, invalidate_first=False)


def _generate_view(drink, user, session, keg):
    """Generates a single "view" (row) based on `drink`."""
    logger.debug('>>> Building stats for drink={}: user={} session={} keg={}'.format(
        drink.id,
        user.username if user else None,
        session.id if session else None,
        keg.id if keg else None))

    # Determine previous drinks in the same view.  This *may* be empty if this
    # is the first drink for the view (first pour on the system, drink, etc.)
    prior_drinks_in_view = models.Drink.objects.filter(id__lt=drink.id)
    if user:
        prior_drinks_in_view = prior_drinks_in_view.filter(user=user.id)
    if session:
        prior_drinks_in_view = prior_drinks_in_view.filter(session=session.id)
    if keg:
        prior_drinks_in_view = prior_drinks_in_view.filter(keg=keg.id)

    prior_drinks_in_view = prior_drinks_in_view.order_by('-id')

    prior_stats = util.AttrDict()
    build_list = [drink]
    if prior_drinks_in_view.count():
        # Starting with the most recent prior drink, get its stats row.
        # If stats don't exist, add drink to build list and continue
        # until a stats row is found or all drinks are exhausted.
        # N.B. we avoid a recursive algorithm due to potentially large recursion
        # depth in certain cases.
        for prior_drink in prior_drinks_in_view:
            try:
                prior_stats = util.AttrDict(
                    models.Stats.objects.get(drink=prior_drink, user=user,
                        session=session, keg=keg).stats
                )
                break
            except models.Stats.DoesNotExist:
                prior_stats = util.AttrDict()
                build_list.insert(0, prior_drink)

    # Build all drinks on the hit list.
    for build_drink in build_list:
        logger.debug('  - operating on drink {}'.format(build_drink.id))
        stats = BUILDER.build(drink=build_drink, previous_stats=prior_stats)
        models.Stats.objects.create(drink=build_drink, user=user, session=session,
            keg=keg, stats=stats, is_first=(not prior_stats))
        prior_stats = stats
    logger.debug('<<< Done.')


def generate(drink, invalidate_first=True):
    """Generates all stats "views" based on `drink`."""
    if invalidate_first:
        invalidate(drink.id)

    # Create an entry for each stats "view".
    for user in (None, drink.user):
        for session in (None, drink.session):
            for keg in (None, drink.keg):
                _generate_view(drink, user, session, keg)

if __name__ == '__main__':
    import cProfile
    command = """main()"""
    cProfile.runctx(command, globals(), locals(), filename="stats.profile")
