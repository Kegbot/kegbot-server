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

from django.conf import settings
from django.core.cache import cache as django_cache

import time

"""Kegbot system cache."""

# Separator
SEP = ':'


class KegbotCache:
    """Wrapper around django cache, supporting Kegbot-specific features.

    Primarily, this wrapper facilitates "generational" or "namespaced" caching,
    using two stages of cache keys: the "generation" key, and individual cache
    keys derived on it (which fall out of the cache as the generation is
    changed).
    """

    def __init__(self, prefix=None, cache=django_cache,
            generation_fn=lambda: int(time.time()),
            generation_key_name='drink_generation'):
        """Constructor.

        Args:
            prefix: If supplied, an additional prefix which will be added to all
                cache keys.  (The global KEGBOT_CACHE_PREFIX is always added).
            cache: Something implementing the django.cache interface (which is
                the default).
            generation_fn: A function which supplies the default value for
                the generation counter.  The function should return an integer.
            generation_key_name: the key name for the "generation", aka
                the namespace.
        """
        global_prefix = getattr(settings, 'KEGBOT_CACHE_PREFIX', 'kb')
        if not prefix:
            self.prefix = global_prefix
        else:
            self.prefix = SEP.join((global_prefix, prefix))
        self.cache = cache
        self.generation_key = SEP.join((self.prefix, generation_key_name))
        self.generation_fn = generation_fn

    def keyname(self, *keyparts):
        """Gets the kegbot-prefixed key name for the given base name."""
        return SEP.join((self.prefix,) + keyparts)

    def get(self, basename, default=None):
        """Wrapper around `self.cache.get()`."""
        return self.cache.get(self.keyname(basename), default)

    def set(self, basename, value, timeout=None):
        """Wrapper around `self.cache.set()`."""
        self.cache.set(self.keyname(basename), value, timeout)

    def add(self, basename, value, timeout=None):
        """Wrapper around `self.cache.add()`."""
        return self.cache.add(self.keyname(basename), value, timeout)

    def incr(self, basename, delta=1):
        """Wrapper around `self.cache.incr()`."""
        return self.cache.incr(self.keyname(basename), delta)

    def decr(self, basename, delta=1):
        """Wrapper around `self.cache.decr()`."""
        return self.cache.decr(self.keyname(basename), delta)

    ### Generational functions.

    def get_generation(self):
        """Returns the value of the current generation.

        Based on:
          https://code.google.com/p/memcached/wiki/NewProgrammingTricks
        """
        generation = self.cache.get(self.generation_key)
        if not generation:
            generation = self.generation_fn()
            if not self.cache.add(self.generation_key, generation):
                # Lost the race.
                generation = self.cache.get(self.generation_key)
        if generation is None:
            raise ValueError('Cache backend returned None')
        return generation

    def update_generation(self):
        """Increments the current generation."""
        self.get_generation()
        try:
            self.cache.incr(self.generation_key, 1)
        except ValueError:
            # Increment failed! Generation must not exist.
            self.cache.add(self.generation_key, self.generation_fn())

    def gen_keyname(self, *keyparts):
        """Like `keyname()`, but returns a key namespaced by the generation."""
        return self.keyname(*(keyparts + (str(self.get_generation()),)))

    def gen_get(self, basename, default=None):
        """Like `get()`, but uses a key namespaced by the generation."""
        return self.get(self.gen_keyname(basename), default)

    def gen_set(self, basename, value, timeout=None):
        """Like `set()`, but uses a key namespaced by the generation."""
        self.set(self.gen_keyname(basename), value, timeout)

    def gen_add(self, basename, value, timeout=None):
        """Like `add()`, but returns a key namespaced by the generation."""
        return self.cache.add(self.gen_keyname(basename), value, timeout)

    def gen_incr(self, basename, delta=1):
        """Like `incr()`, but returns a key namespaced by the generation."""
        return self.cache.incr(self.gen_keyname(basename), delta)

    def gen_decr(self, basename, delta=1):
        """Like `decr()`, but returns a key namespaced by the generation."""
        return self.cache.decr(self.gen_keyname(basename), delta)
