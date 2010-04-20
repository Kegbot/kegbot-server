#!/usr/bin/env python
#
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

"""Post-drink Facebook annoy-o-matic."""

from pykeg.core import kb_app
from pykeg.core import models
from pykeg.core.net import kegnet
from pykeg.contrib.facebook import fbutil

class FBKegnetClient(kegnet.SimpleKegnetClient):
  def onDrinkCreated(self, event):
    self._logger.info('Drink created: %s' % event)

    # TODO(mikey): this should not be allowed to use the DB directly. Quick hack
    # for now..
    drink = models.Drink.objects.get(id=event.drink_id)
    self._AnotherBeerOnTheWall(drink)

  def _AnotherBeerOnTheWall(self, drink):
    user = drink.user
    profile = fbutil.profile_for_user(user)
    if not profile:
      self._logger.info('No profile for user %s' % user)
      return

    session = fbutil.session_for_user(user)
    if not session:
      self._logger.info('No facebook session for user %s' % user)
      return

    settings = fbutil.settings_for_user(user)
    if not settings:
      self._logger.info('No facebook settings for user %s' % user)
      return

    if not settings.publish_events:
      self._logger.info('Publishing disabled by user\'s settings.')
      return

    # Format the message
    if drink.keg and drink.keg.type.name:
      beer_name = drink.keg.type.name
    else:
      beer_name = 'beer'

    ounces = drink.Volume().ConvertTo.Ounce
    message = 'just poured %(ounces).1f ounces of %(beer_name)s from Kegbot.' % vars()

    action_links = [
      {
        'text': 'View Drink',
        'href': drink.ShortUrl(),
      }
    ]

    privacy = settings.privacy

    # TODO(mikey): pyfacebook streamPublish does not support privacy (?)
    fbutil.stream_publish(user, message=message,
        action_links=action_links)


class FacebookApp(kb_app.App):
  def _MainLoop(self):
    self._client = FBKegnetClient()
    while not self._do_quit:
      self._client.serve_forever()

  def Quit(self):
    kb_app.App.Quit(self)
    self._client.stop()
