# Copyright 2013 Mike Wakerly <opensource@hoho.com>
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

"""Celery tasks for Webhook plugin."""

from celery.task import task
from pykeg.plugin import util
from pykeg.proto import protolib
from kegbot.util import kbjson
from urllib import urlencode
import urllib2

logger = util.get_logger(__name__)

@task(expires=180)
def post_webhook(url, event):
    """Posts an event to the supplied URL."""
    logger.info('Posting webhook: url=%s event=%s' % (url, event))
    post_data = kbjson.dumps({'events': [protolib.ToDict(event)]})
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
