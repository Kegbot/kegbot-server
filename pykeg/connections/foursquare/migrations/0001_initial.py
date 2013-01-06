# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'FoursquareProfile'
        db.create_table('foursquare_foursquareprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], unique=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sites.Site'])),
            ('foursquare', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('foursquare', ['FoursquareProfile'])

        # Adding model 'FoursquareAccessToken'
        db.create_table('foursquare_foursquareaccesstoken', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('profile', self.gf('django.db.models.fields.related.OneToOneField')(related_name='access_token', unique=True, to=orm['foursquare.FoursquareProfile'])),
            ('access_token', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('foursquare', ['FoursquareAccessToken'])

        # Adding model 'SiteFoursquareSettings'
        db.create_table('foursquare_sitefoursquaresettings', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('site', self.gf('django.db.models.fields.related.OneToOneField')(related_name='foursquare_settings', unique=True, to=orm['core.KegbotSite'])),
            ('venue_id', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('venue_name', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal('foursquare', ['SiteFoursquareSettings'])

        # Adding model 'FoursquareSettings'
        db.create_table('foursquare_foursquaresettings', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('profile', self.gf('django.db.models.fields.related.OneToOneField')(related_name='settings', unique=True, to=orm['foursquare.FoursquareProfile'])),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('checkin_session_joined', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('foursquare', ['FoursquareSettings'])


    def backwards(self, orm):
        
        # Deleting model 'FoursquareProfile'
        db.delete_table('foursquare_foursquareprofile')

        # Deleting model 'FoursquareAccessToken'
        db.delete_table('foursquare_foursquareaccesstoken')

        # Deleting model 'SiteFoursquareSettings'
        db.delete_table('foursquare_sitefoursquaresettings')

        # Deleting model 'FoursquareSettings'
        db.delete_table('foursquare_foursquaresettings')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'core.kegbotsite': {
            'Meta': {'object_name': 'KegbotSite'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'})
        },
        'foursquare.foursquareaccesstoken': {
            'Meta': {'object_name': 'FoursquareAccessToken'},
            'access_token': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'profile': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'access_token'", 'unique': 'True', 'to': "orm['foursquare.FoursquareProfile']"})
        },
        'foursquare.foursquareprofile': {
            'Meta': {'object_name': 'FoursquareProfile'},
            'foursquare': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'foursquare.foursquaresettings': {
            'Meta': {'object_name': 'FoursquareSettings'},
            'checkin_session_joined': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'profile': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'settings'", 'unique': 'True', 'to': "orm['foursquare.FoursquareProfile']"})
        },
        'foursquare.sitefoursquaresettings': {
            'Meta': {'object_name': 'SiteFoursquareSettings'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'site': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'foursquare_settings'", 'unique': 'True', 'to': "orm['core.KegbotSite']"}),
            'venue_id': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'venue_name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['foursquare']
