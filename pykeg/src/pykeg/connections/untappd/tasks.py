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
from pykeg.connections.foursquare import models as foursquare_models
from django.contrib.sites.models import Site
from . import models
from django.conf import settings

from urllib import urlencode
import urllib2
import base64

from celery.decorators import task

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
  if should_checkin(event):
    do_checkin(event)
    return True
  return False

def should_checkin(event):
  if event.kind not in ('drink_poured'):
    print 'Event not checkin-able: %s' % event
    return False
  return True

def _get_vars(event):
  base_url = 'http://%s/%s' % (Site.objects.get_current().domain, event.site.url())
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
    'kb_name': event.site.settings.title,
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
    print 'Untappd beer id is not specified for this beer.'
    return

  ounces = drink.Volume().InOunces()
  
  min_ounces = 2.0
  
  if ounces < min_ounces:
    print 'Drink too small to care about; no untappd checkin for you!'
    return

  if event.user:
    try:
      db_user = core_models.User.objects.get(username=event.user.username)
      profile = db_user.get_profile()
    except (core_models.User.DoesNotExist, core_models.UserProfile.DoesNotExist):
      print 'Profile for user %s does not exist' % drink.user
      return
    try:
      untappd_link = models.UserUntappdLink.objects.get(user_profile=profile)

    except models.UserUntappdLink.DoesNotExist:
      # Untappd name unknown
      print 'User %s has not enabled untappd link.' % drink.user
      return

  try:
    site_4sq_settings = foursquare_models.SiteFoursquareSettings.objects.get(site=event.site)
    #venue_id = site_4sq_settings.venue_id
    venue_id = ''
  except foursquare_models.SiteFoursquareSettings.DoesNotExist:
    venue_id = ''

  kbvars = _get_vars(event)

  shout = DEFAULT_CHECKIN_TEMPLATE % kbvars

  params = {
    'bid': beerid,
    'gmt_offset': settings.GMT_OFFSET,
    'shout': shout,
  }

  if venue_id:
    params['foursquare_id'] = venue_id

  params = urlencode(params)
  req = urllib2.Request("http://api.untappd.com/v3/checkin?key=" + settings.UNTAPPD_API_KEY, params)

  base64string = base64.encodestring('%s:%s' % (untappd_link.untappd_name, untappd_link.untappd_password_hash))[:-1]
  authheader =  "Basic %s" % base64string
  req.add_header("Authorization", authheader)

  response = urllib2.urlopen(req)

  print response.read()
