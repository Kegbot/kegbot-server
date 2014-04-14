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
import itertools
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
            username = str(drink.user.username)
            if username not in ret:
                ret.append(username)
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
        u = drink.user.username
        orig = ret.get(u, 0)
        ret[u] = float(orig + drink.volume_ml)
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
    """Clears all statistics since (and including) drink_id."""
    logger.debug('--- Invalidating stats since id {}'.format(drink_id))
    models.Stats.objects.filter(drink_id__gte=drink_id).delete()

def invalidate_all():
    logger.debug('--- Invalidating ALL stats')
    models.Stats.objects.all().delete()

def rebuild_from_id(drink_id):
    invalidate(drink_id)
    for drink in models.Drink.objects.filter(id__gte=drink_id).order_by('id'):
        generate(drink, invalidate_first=False)

def _generate_view(drink, previous_drink, user, session, keg):
    """Generates a single "view" (row) based on `drink`."""
    logger.debug('>>> Building stats for drink={}: user={} session={} keg={}'.format(
        drink.id,
        user.username if user else None,
        session.id if session else None,
        keg.id if keg else None))

    # Determine previous drink with same view.  This *may* be empty if this is
    # the first drink for the view (first pour on the system, drink, etc.)
    qs = models.Drink.objects.filter(id__lt=drink.id)
    if user:
        qs = qs.filter(user=user.id)
    if session:
        qs = qs.filter(session=session.id)
    if keg:
        qs = qs.filter(keg=keg.id)

    try:
        previous_drink = qs.order_by('-id')[0]
    except IndexError:
        previous_drink = None

    # There's a previous drink in this view, so fetch its stats record to use
    # as the basis for this record. This *will* fail if the db is incoherent
    # (ie if there are gaps in stats table).
    previous_stats = util.AttrDict()
    if previous_drink:
        previous_row = models.Stats.objects.get(drink=previous_drink, user=user,
            session=session, keg=keg)
        previous_stats = util.AttrDict(previous_row.stats)

    stats = BUILDER.build(drink=drink, previous_stats=previous_stats)
    ret = models.Stats.objects.create(drink=drink, user=user, session=session,
        keg=keg, stats=stats, is_first=(previous_drink is None))
    logger.debug('<<< Done.')
    return ret

def generate(drink, previous_drink=None, invalidate_first=True):
    """Generates all stats "views" based on `drink`."""
    if invalidate_first:
        invalidate(drink.id)

    if not previous_drink:
        previous_drinks = models.Drink.objects.filter(id__lt=drink.id).order_by('-id')
        if previous_drinks:
            previous_drink = previous_drinks[0]

    # Create an entry for each stats "view".
    for user in (None, drink.user):
        for session in (None, drink.session):
            for keg in (None, drink.keg):
                _generate_view(drink, previous_drink, user, session, keg)

if __name__ == '__main__':
    import cProfile
    command = """main()"""
    cProfile.runctx( command, globals(), locals(), filename="stats.profile" )
