from __future__ import absolute_import

"""Celery beat scheduler backed by Redis.

The schedule will be saved as a pickled data in the key
'celery:beat:<filename>', where filename is the schedule filename
configured in celery

Prerequisite:
  You are using Redis as your broker (BROKER_URL = 'redis://...')

Usage:
  CELERYBEAT_SCHEDULER = 'module.celery.RedisScheduler'
"""

__author__ = 'opensource@hoho.com'

import logging
import pickle

from celery.beat import PersistentScheduler


class RedisShelve(object):
    """Implements the `shelve` interface by pickling to a redis entry."""

    def __init__(self, connection, key_prefix='celery:beat:'):
        self.logger = logging.getLogger(__name__)
        self._connection = connection
        self._key_prefix = key_prefix

        self._filename = None
        self._d = {}

    def open(self, filename, writeback=False, **kwargs):
        assert not self._filename, 'Already open'
        assert not kwargs, 'Unknown arguments: {}'.format(kwargs)

        self._redis_key = '{}{}'.format(self._key_prefix, filename)
        self.logger.debug('open: {}'.format(self._redis_key))

        data = self._connection.get(self._redis_key)
        try:
            data_dict = pickle.loads(data)
        except (EOFError, ValueError, TypeError) as e:
            self.logger.warning('Empty/corrupt persisted data: {}'.format(e))
            data_dict = {}

        class wrapped(dict):
            pass
        wrapped.sync = self.sync
        wrapped.close = self.close

        self._d = wrapped(data_dict)
        return self._d

    def sync(self):
        self.logger.debug('sync: {}'.format(self._d))
        data = pickle.dumps(dict(self._d))
        self._connection.set(self._redis_key, data)

    def close(self):
        self.logger.debug('close')
        self.sync()
        self._d = {}
        self._filename = None


class RedisScheduler(PersistentScheduler):
    """Scheduler that uses a RedisShelve for storage."""

    def __init__(self, *args, **kwargs):
        app = kwargs['app']
        self.persistence = RedisShelve(app.backend.client)
        PersistentScheduler.__init__(self, *args, **kwargs)
