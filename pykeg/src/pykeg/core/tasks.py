# Copyright 2011 Mike Wakerly <opensource@hoho.com>
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

"""Celery tasks for the Kegbot core."""

from pykeg.core import kbjson

from urllib import urlencode
import urllib2

from celery.decorators import task

@task
def post_webhook_event(hook_url, event_list):
  post_data = kbjson.dumps({'events': event_list})
  post_data = urlencode({'payload': post_data})
  # TODO(mikey): set user agent to Kegbot.
  urllib2.urlopen(hook_url, data=post_data)
  return True

