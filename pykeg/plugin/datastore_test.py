from django.test import TransactionTestCase

from pykeg.core import models
from pykeg.plugin import datastore


class DatastoreTestCase(TransactionTestCase):
    def test_model_datastore(self):
        ds = datastore.ModelDatastore(plugin_name="test")

        self.assertEqual(0, models.PluginData.objects.all().count())

        ds.set("foo", "bar")
        q = models.PluginData.objects.all()
        self.assertEqual(1, q.count())
        self.assertEqual("test", q[0].plugin_name)
        self.assertEqual("foo", q[0].key)
        self.assertEqual("bar", q[0].value)

        # Setting to 'None' clears value
        ds.set("foo", None)
        self.assertEqual(0, models.PluginData.objects.all().count())

        # Complex types survive.
        ds.set("obj", {"asdf": 123, "foo": None})
        self.assertEqual({"asdf": 123, "foo": None}, ds.get("obj"))

    def test_in_memory_datastore(self):
        ds = datastore.InMemoryDatastore(plugin_name="test")

        self.assertEqual(0, len(ds.data))

        ds.set("foo", "bar")
        self.assertEqual(1, len(ds.data))
        self.assertEqual("bar", ds.data["test:foo"])

        # Setting to 'None' clears value
        ds.set("foo", None)
        self.assertEqual(0, len(ds.data))

        # Complex types survive.
        ds.set("obj", {"asdf": 123, "foo": None})
        self.assertEqual({"asdf": 123, "foo": None}, ds.get("obj"))
