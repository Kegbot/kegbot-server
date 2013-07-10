# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'PluginData'
        db.create_table(u'plugin_plugindata', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('plugin_name', self.gf('django.db.models.fields.CharField')(max_length=127)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=127)),
            ('value', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'plugin', ['PluginData'])

        # Adding unique constraint on 'PluginData', fields ['plugin_name', 'key']
        db.create_unique(u'plugin_plugindata', ['plugin_name', 'key'])


    def backwards(self, orm):
        # Removing unique constraint on 'PluginData', fields ['plugin_name', 'key']
        db.delete_unique(u'plugin_plugindata', ['plugin_name', 'key'])

        # Deleting model 'PluginData'
        db.delete_table(u'plugin_plugindata')


    models = {
        u'plugin.plugindata': {
            'Meta': {'unique_together': "(('plugin_name', 'key'),)", 'object_name': 'PluginData'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '127'}),
            'plugin_name': ('django.db.models.fields.CharField', [], {'max_length': '127'}),
            'value': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['plugin']