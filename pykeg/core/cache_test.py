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

from django.core.cache import cache as django_cache
from django.test import TransactionTestCase
from django.test.utils import override_settings

from .cache import KegbotCache


class KegbotCacheTest(TransactionTestCase):

    def setUp(self):
        django_cache.clear()

    def test_basics(self):
        cache = KegbotCache(generation_fn=lambda: 100)

        # keyname, get, set
        self.assertEquals('kb:foo', cache.keyname('foo'))
        self.assertEquals(None, django_cache.get('kb:foo'))
        self.assertEquals(123, django_cache.get('kb:foo', 123))
        cache.set('foo', 'bar')
        self.assertEquals('bar', django_cache.get('kb:foo'))

        # generation
        self.assertEquals(None, django_cache.get(cache.generation_key))
        gen = cache.get_generation()
        self.assertEquals(100, gen)
        self.assertEquals('kb:foo:100', cache.gen_keyname('foo'))
        self.assertEquals(100, django_cache.get(cache.generation_key))

        cache.gen_set('test', 555)
        self.assertEquals(555, cache.gen_get('test'))
        cache.update_generation()
        self.assertEquals(101, cache.get_generation())
        self.assertEquals(None, cache.gen_get('test'))

    @override_settings(KEGBOT_CACHE_PREFIX='other')
    def test_prefix_other(self):
        """Verifies settings.KEGBOT_CACHE_PREFIX is respected."""
        cache = KegbotCache(generation_fn=lambda: 100)
        self.assertEquals('other:foo', cache.keyname('foo'))
        self.assertEquals('other:foo:100', cache.gen_keyname('foo'))

    def test_generation_update(self):
        """Tests updating the generation succeeds even when missing."""
        cache = KegbotCache(generation_fn=lambda: 100)
        cache.update_generation()
