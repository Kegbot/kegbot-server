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

from kegbot.util import util
from kegbot.util import kbjson

from pykeg.core import models
from pykeg.proto import protolib

from pykeg.connections import tasks as connection_tasks

from urllib import urlencode
import urllib2

from celery.decorators import task

@task
def post_webhook_event(hook_url, event_list):
  post_data = kbjson.dumps({'events': [protolib.ToDict(e) for e in event_list]})
  post_data = urlencode({'payload': post_data})
  opener = urllib2.build_opener()
  opener.addheaders = [
    ('User-agent', 'Kegbot/%s' % util.get_version('kegbot')),
  ]
  try:
    opener.open(hook_url, data=post_data, timeout=5)
    return True
  except urllib2.URLError:
    return False

@task
def handle_new_events(event_list):
  web_hook_urls = models.SiteSettings.get().web_hook_urls
  if web_hook_urls:
    urls = [u for u in web_hook_urls.split() if u]
    for url in urls:
      post_webhook_event.delay(url, event_list)

  for event in event_list:
    connection_tasks.handle_new_event.delay(event)

  return True

@task
def handle_new_picture(picture_id):
  connection_tasks.handle_new_picture.delay(picture_id)
