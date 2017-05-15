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

"""Celery tasks for Yo plugin."""

from pykeg.celery import app
from pykeg.plugin import util
from pykeg.core.util import get_version

import requests

logger = util.get_logger(__name__)

@app.task(name='yo_post', expires=180)
def yo_post(api_token):
    """
		Posts the api_token to yo
    """
    url = "http://api.justyo.co/yoall/"
    logger.info('Posting yo: url=%s api_token=%s' % (url, api_token))

    payload = {
        'api_token': api_token,
    }

    headers = {
        'user-agent': 'Kegbot/%s' % get_version(),
    }

    try:
        return requests.post(url, data=payload, headers=headers)
    except requests.exceptions.RequestException, e:
        logger.warning('Error posting yo: %s' % e)
        return False
