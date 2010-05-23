# -*- coding: latin-1 -*-

from south.db import db
from django.db import models
from pykeg.contrib.soundserver.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'SoundEvent'
        db.create_table('soundserver_soundevent', (
            ('id', orm['soundserver.SoundEvent:id']),
            ('event_name', orm['soundserver.SoundEvent:event_name']),
            ('event_predicate', orm['soundserver.SoundEvent:event_predicate']),
            ('soundfile', orm['soundserver.SoundEvent:soundfile']),
            ('user', orm['soundserver.SoundEvent:user']),
        ))
        db.send_create_signal('soundserver', ['SoundEvent'])
        
        # Adding model 'SoundFile'
        db.create_table('soundserver_soundfile', (
            ('id', orm['soundserver.SoundFile:id']),
            ('sound', orm['soundserver.SoundFile:sound']),
            ('title', orm['soundserver.SoundFile:title']),
            ('active', orm['soundserver.SoundFile:active']),
        ))
        db.send_create_signal('soundserver', ['SoundFile'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'SoundEvent'
        db.delete_table('soundserver_soundevent')
        
        # Deleting model 'SoundFile'
        db.delete_table('soundserver_soundfile')
        
    
    
    models = {
        'auth.group': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)"},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'soundserver.soundevent': {
            'event_name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'event_predicate': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'soundfile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['soundserver.SoundFile']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'soundserver.soundfile': {
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sound': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        }
    }
    
    complete_apps = ['soundserver']
