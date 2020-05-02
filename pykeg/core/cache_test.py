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
        self.assertEqual("kb:foo", cache.keyname("foo"))
        self.assertEqual(None, django_cache.get("kb:foo"))
        self.assertEqual(123, django_cache.get("kb:foo", 123))
        cache.set("foo", "bar")
        self.assertEqual("bar", django_cache.get("kb:foo"))

        # generation
        self.assertEqual(None, django_cache.get(cache.generation_key))
        gen = cache.get_generation()
        self.assertEqual(100, gen)
        self.assertEqual("kb:foo:100", cache.gen_keyname("foo"))
        self.assertEqual(100, django_cache.get(cache.generation_key))

        cache.gen_set("test", 555)
        self.assertEqual(555, cache.gen_get("test"))
        cache.update_generation()
        self.assertEqual(101, cache.get_generation())
        self.assertEqual(None, cache.gen_get("test"))

    @override_settings(KEGBOT_CACHE_PREFIX="other")
    def test_prefix_other(self):
        """Verifies settings.KEGBOT_CACHE_PREFIX is respected."""
        cache = KegbotCache(generation_fn=lambda: 100)
        self.assertEqual("other:foo", cache.keyname("foo"))
        self.assertEqual("other:foo:100", cache.gen_keyname("foo"))

    def test_generation_update(self):
        """Tests updating the generation succeeds even when missing."""
        cache = KegbotCache(generation_fn=lambda: 100)
        cache.update_generation()
