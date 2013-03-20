# Copyright 2012 Mike Wakerly <opensource@hoho.com>
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

import logging

from pykeg.core import features
from pykeg.connections.foursquare import tasks as foursquare_tasks
from pykeg.connections.twitter import tasks as twitter_tasks
from pykeg.connections.untappd import tasks as untappd_tasks
from celery.decorators import task
from celery.utils.log import get_task_logger

LOGGER = get_task_logger(__name__)

@task
def handle_new_event(event):
  if features.use_twitter():
    LOGGER.info('handle_new_event: dispatching to twitter ..')
    twitter_tasks.tweet_event(event)
  else:
    LOGGER.info('handle_new_event: twitter not enabled, skipping.')

  if features.use_foursquare():
    LOGGER.info('handle_new_event: dispatching to foursquare ..')
    foursquare_tasks.checkin_event(event)
  else:
    LOGGER.info('handle_new_event: foursquare not enabled, skipping.')

  if features.use_untappd():
    LOGGER.info('handle_new_event: dispatching to untappd ..')
    untappd_tasks.checkin_event(event)
  else:
    LOGGER.info('handle_new_event: untappd not enabled, skipping.')

@task
def handle_new_picture(picture_id):
  if features.use_foursquare():
    LOGGER.info('handle_new_picture: dispatching to foursquare ..')
    foursquare_tasks.handle_new_picture(picture_id)
  else:
    LOGGER.info('handle_new_picture: foursquare not enabled, skipping.')

