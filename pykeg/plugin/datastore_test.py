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

from django.test import TransactionTestCase

from pykeg.plugin import datastore
from pykeg.core import models


class DatastoreTestCase(TransactionTestCase):

    def test_model_datastore(self):
        ds = datastore.ModelDatastore(plugin_name='test')

        self.assertEqual(0, models.PluginData.objects.all().count())

        ds.set('foo', 'bar')
        q = models.PluginData.objects.all()
        self.assertEqual(1, q.count())
        self.assertEqual('test', q[0].plugin_name)
        self.assertEqual('foo', q[0].key)
        self.assertEqual('bar', q[0].value)

        # Setting to 'None' clears value
        ds.set('foo', None)
        self.assertEqual(0, models.PluginData.objects.all().count())

        # Complex types survive.
        ds.set('obj', {'asdf': 123, 'foo': None})
        self.assertEqual({'asdf': 123, 'foo': None}, ds.get('obj'))

    def test_in_memory_datastore(self):
        ds = datastore.InMemoryDatastore(plugin_name='test')

        self.assertEqual(0, len(ds.data))

        ds.set('foo', 'bar')
        self.assertEqual(1, len(ds.data))
        self.assertEqual('bar', ds.data['test:foo'])

        # Setting to 'None' clears value
        ds.set('foo', None)
        self.assertEqual(0, len(ds.data))

        # Complex types survive.
        ds.set('obj', {'asdf': 123, 'foo': None})
        self.assertEqual({'asdf': 123, 'foo': None}, ds.get('obj'))
