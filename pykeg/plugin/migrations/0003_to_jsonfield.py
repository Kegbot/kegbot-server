# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'PluginData.value'
        db.alter_column(u'plugin_plugindata', 'value', self.gf('pykeg.core.jsonfield.JSONField')())

    def backwards(self, orm):

        # Changing field 'PluginData.value'
        db.alter_column(u'plugin_plugindata', 'value', self.gf('django.db.models.fields.TextField')())

    models = {
        u'plugin.plugindata': {
            'Meta': {'unique_together': "(('plugin_name', 'key'),)", 'object_name': 'PluginData'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '127'}),
            'plugin_name': ('django.db.models.fields.CharField', [], {'max_length': '127'}),
            'value': ('pykeg.core.jsonfield.JSONField', [], {})
        }
    }

    complete_apps = ['plugin']