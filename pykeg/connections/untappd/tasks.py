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

"""Celery tasks for Untappd."""

from pykeg.core import models as core_models
from pykeg.connections import common
from pykeg.connections.foursquare import models as foursquare_models
from django.contrib.sites.models import Site
from pykeg.connections.untappd import models

from django.conf import settings
from django.utils import timezone

from urllib import urlencode
import urllib2

from celery.task import task

logger = common.get_logger(__name__)

# Available template vars:
#   name         : user name, or @twitter_name if known
#   kb_name      : kegbot system name
#   kb_url       : kegbot system url
#   session_url  : current session url
#   drink_url    : drink url (if any)
#   drink_size   : drink size
#   beer_name    : beer name

DEFAULT_CHECKIN_TEMPLATE = "Automatic checkin courtesy of %(kb_name)s! %(drink_url)s"

@task
def checkin_event(event):
  if event.kind not in ('drink_poured',):
    logger.info('Event not suitable for checkin: %s' % event.kind)
    return
  do_checkin(event)

def _get_vars(event):
  settings = core_models.SiteSettings.get()
  base_url = settings.base_url()
  name = ''
  if event.user:
    name = event.user.username
  session_url = ''
  drink_url = ''

  if event.drink:
    session_url = '%s/%s' % (base_url, event.drink.session.get_absolute_url())
    drink_url = event.drink.ShortUrl()

  beer_name = ''
  if event.drink.keg and event.drink.keg.type:
    beer_name = event.drink.keg.type.name

  drink_size = ''
  if event.drink:
    drink_size = '%.1foz' % event.drink.Volume().InOunces()

  kbvars = {
    'kb_name': settings.title,
    'name': name,
    'kb_url': base_url,
    'drink_url': drink_url,
    'session_url': session_url,
    'drink_size': drink_size,
    'beer_name': beer_name,
  }
  return kbvars

def do_checkin(event):
  drink = event.drink

  beerid = drink.keg.type.untappd_beer_id

  if beerid == None:
    logger.info('Untappd beer id is not specified for this beer.')
    return

  ounces = drink.Volume().InOunces()

  min_ounces = 2.0

  if ounces < min_ounces:
    logger.info('Drink too small to care about; no untappd checkin for you!')
    return

  access_token = None
  if event.user:
    try:
      db_user = core_models.User.objects.get(username=event.user.username)
    except (core_models.User.DoesNotExist):
      logger.info('Profile for user %s does not exist' % drink.user)
      return

    try:
      user_profile = models.UntappdProfile.objects.get(user=db_user)
      access_token = user_profile.access_token.access_token
    except (models.UntappdProfile.DoesNotExist):
      # Untappd name unknown
      logger.info('User %s has not enabled untappd link.' % drink.user)
      return

  if not access_token:
    logger.info('No access token for user %s.' % drink.user)
    return

  try:
    site_4sq_settings = foursquare_models.SiteFoursquareSettings.objects.get(site=event.site)
    #venue_id = site_4sq_settings.venue_id
    venue_id = ''
  except foursquare_models.SiteFoursquareSettings.DoesNotExist:
    venue_id = ''

  kbvars = _get_vars(event)

  shout = DEFAULT_CHECKIN_TEMPLATE % kbvars

  gmt_offset = timezone.localtime(timezone.now()).utcoffset()
  gmt_offset_hours = (gmt_offset.days * 86400 + gmt_offset.seconds) / 3600

  params = {
    'bid': beerid,
    'gmt_offset': gmt_offset_hours,
    'shout': shout,
    'access_token': access_token,
    'client_id': settings.UNTAPPD_CLIENT_ID,
    'client_secret': settings.UNTAPPD_CLIENT_SECRET,
    'timezone': settings.TIME_ZONE
  }

  if venue_id:
    params['foursquare_id'] = venue_id

  params = urlencode(params)
  req = urllib2.Request("http://api.untappd.com/v4/checkin/add?" + params, params)

  response = urllib2.urlopen(req)

  response = response.read()
  logger.info('Response: %s' % str(response))
