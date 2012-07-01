# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SiteTwitterProfile'
        db.create_table('twitter_sitetwitterprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('site', self.gf('django.db.models.fields.related.OneToOneField')(related_name='twitter_profile', unique=True, to=orm['core.KegbotSite'])),
            ('twitter_name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('twitter_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('oauth_token', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('oauth_token_secret', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('twitter', ['SiteTwitterProfile'])

        # Adding model 'SiteTwitterSettings'
        db.create_table('twitter_sitetwittersettings', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('post_session_joined', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('post_drink_poured', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('profile', self.gf('django.db.models.fields.related.OneToOneField')(related_name='settings', unique=True, to=orm['twitter.SiteTwitterProfile'])),
        ))
        db.send_create_signal('twitter', ['SiteTwitterSettings'])

        # Adding model 'TwitterProfile'
        db.create_table('twitter_twitterprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], unique=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sites.Site'])),
            ('twitter_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('twitter', ['TwitterProfile'])

        # Adding model 'TwitterRequestToken'
        db.create_table('twitter_twitterrequesttoken', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('profile', self.gf('django.db.models.fields.related.OneToOneField')(related_name='request_token', unique=True, to=orm['twitter.TwitterProfile'])),
            ('oauth_token', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('oauth_token_secret', self.gf('django.db.models.fields.CharField')(max_length=80)),
        ))
        db.send_create_signal('twitter', ['TwitterRequestToken'])

        # Adding model 'TwitterAccessToken'
        db.create_table('twitter_twitteraccesstoken', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('profile', self.gf('django.db.models.fields.related.OneToOneField')(related_name='access_token', unique=True, to=orm['twitter.TwitterProfile'])),
            ('oauth_token', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('oauth_token_secret', self.gf('django.db.models.fields.CharField')(max_length=80)),
        ))
        db.send_create_signal('twitter', ['TwitterAccessToken'])

        # Adding model 'TwitterSettings'
        db.create_table('twitter_twittersettings', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('post_session_joined', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('post_drink_poured', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('profile', self.gf('django.db.models.fields.related.OneToOneField')(related_name='settings', unique=True, to=orm['twitter.TwitterProfile'])),
            ('twitter_name', self.gf('django.db.models.fields.CharField')(max_length=64)),
        ))
        db.send_create_signal('twitter', ['TwitterSettings'])

    def backwards(self, orm):
        # Deleting model 'SiteTwitterProfile'
        db.delete_table('twitter_sitetwitterprofile')

        # Deleting model 'SiteTwitterSettings'
        db.delete_table('twitter_sitetwittersettings')

        # Deleting model 'TwitterProfile'
        db.delete_table('twitter_twitterprofile')

        # Deleting model 'TwitterRequestToken'
        db.delete_table('twitter_twitterrequesttoken')

        # Deleting model 'TwitterAccessToken'
        db.delete_table('twitter_twitteraccesstoken')

        # Deleting model 'TwitterSettings'
        db.delete_table('twitter_twittersettings')

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
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'twitter.sitetwitterprofile': {
            'Meta': {'object_name': 'SiteTwitterProfile'},
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'oauth_token': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'oauth_token_secret': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'site': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'twitter_profile'", 'unique': 'True', 'to': "orm['core.KegbotSite']"}),
            'twitter_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'twitter_name': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'twitter.sitetwittersettings': {
            'Meta': {'object_name': 'SiteTwitterSettings'},
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'post_drink_poured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'post_session_joined': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'profile': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'settings'", 'unique': 'True', 'to': "orm['twitter.SiteTwitterProfile']"})
        },
        'twitter.twitteraccesstoken': {
            'Meta': {'object_name': 'TwitterAccessToken'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'oauth_token': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'oauth_token_secret': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'profile': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'access_token'", 'unique': 'True', 'to': "orm['twitter.TwitterProfile']"})
        },
        'twitter.twitterprofile': {
            'Meta': {'object_name': 'TwitterProfile'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'twitter_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'twitter.twitterrequesttoken': {
            'Meta': {'object_name': 'TwitterRequestToken'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'oauth_token': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'oauth_token_secret': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'profile': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'request_token'", 'unique': 'True', 'to': "orm['twitter.TwitterProfile']"})
        },
        'twitter.twittersettings': {
            'Meta': {'object_name': 'TwitterSettings'},
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'post_drink_poured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'post_session_joined': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'profile': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'settings'", 'unique': 'True', 'to': "orm['twitter.TwitterProfile']"}),
            'twitter_name': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        }
    }

    complete_apps = ['twitter']