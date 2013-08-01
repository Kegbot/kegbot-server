# Copyright 2003-2012 Mike Wakerly <opensource@hoho.com>
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
import traceback
import datetime

from collections import deque

PREFIX = 'pykeg.core.logger:'
CACHED_LOGS_KEY = PREFIX + 'buffer'

class CacheHandler(logging.Handler):
    """An exception log handler that buffers errors in the Django cache for future
    processing.
    """
    def __init__(self, max_entries=10):
        logging.Handler.__init__(self)
        self.max_entries = max_entries

    def emit(self, record):
        """Adds the record to the cache."""
        from django.core.cache import cache
        cached_entries = get_cached_logs()
        if cached_entries is not None:
            entries = cached_entries
        else:
            entries = deque()

        # Oldest entries on the left.
        while len(entries) >= self.max_entries:
            entries.pop()

        entries.appendleft(format_record(record))
        cache.set(CACHED_LOGS_KEY, entries)

def format_record(record):
    from django.conf import settings
    ret = {}

    ret['when'] = datetime.datetime.now()
    ret['level'] = record.levelname
    ret['summary'] = record.getMessage()

    if hasattr(record, 'request'):
        request = record.request
        ret['addr'] = request.META.get('REMOTE_ADDR')
        ret['request_path'] = request.path
        ret['method'] = request.method
        if hasattr(request, 'user'):
            ret['username'] = request.user.username
        else:
            ret['usernmae'] = ''
    else:
        ret['addr'] = ''
        ret['request_path'] = ''
        ret['method'] = ''
        ret['username'] = ''

    if record.exc_info:
        ret['exc_text'] = '\n'.join(traceback.format_exception(*record.exc_info))
    else:
        ret['exc_text'] = ''

    return ret

class RequireDebugTrue(logging.Filter):
    def filter(self, record):
        from django.conf import settings
        return settings.DEBUG

def get_cached_logs():
    from django.core.cache import cache
    return cache.get(CACHED_LOGS_KEY)
