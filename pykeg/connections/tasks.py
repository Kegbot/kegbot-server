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

from pykeg.connections.foursquare import tasks as foursquare_tasks
from pykeg.connections.twitter import tasks as twitter_tasks
from pykeg.connections.untappd import tasks as untappd_tasks
from celery.decorators import task

@task
def handle_new_event(event):
  twitter_tasks.tweet_event(event)
  foursquare_tasks.checkin_event(event)
  untappd_tasks.checkin_event(event)

@task
def handle_new_picture(picture_id):
  foursquare_tasks.handle_new_picture(picture_id)
