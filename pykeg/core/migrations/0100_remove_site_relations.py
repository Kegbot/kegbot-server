# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'UserStats', fields ['site', 'user']
        db.delete_unique(u'core_userstats', ['site_id', 'user_id'])

        # Deleting field 'SystemEvent.site'
        db.delete_column(u'core_systemevent', 'site_id')

        # Deleting field 'Keg.site'
        db.delete_column(u'core_keg', 'site_id')


        # Changing field 'Keg.type'
        db.alter_column(u'core_keg', 'type_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.BeerType'], on_delete=models.PROTECT))

        # Changing field 'Keg.size'
        db.alter_column(u'core_keg', 'size_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.KegSize'], on_delete=models.PROTECT))
        # Deleting field 'KegStats.site'
        db.delete_column(u'core_kegstats', 'site_id')

        # Deleting field 'UserStats.site'
        db.delete_column(u'core_userstats', 'site_id')

        # Adding unique constraint on 'UserStats', fields ['user']
        db.create_unique(u'core_userstats', ['user_id'])


        # Changing field 'BeerType.image'
        db.alter_column(u'core_beertype', 'image_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.SET_NULL, to=orm['core.Picture']))
        # Deleting field 'Picture.site'
        db.delete_column(u'core_picture', 'site_id')


        # Changing field 'Brewer.image'
        db.alter_column(u'core_brewer', 'image_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.SET_NULL, to=orm['core.Picture']))
        # Deleting field 'KegTap.site'
        db.delete_column(u'core_kegtap', 'site_id')


        # Changing field 'KegTap.temperature_sensor'
        db.alter_column(u'core_kegtap', 'temperature_sensor_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.ThermoSensor'], null=True, on_delete=models.SET_NULL))
        # Deleting field 'DrinkingSession.site'
        db.delete_column(u'core_drinkingsession', 'site_id')

        # Deleting field 'Drink.site'
        db.delete_column(u'core_drink', 'site_id')


        # Changing field 'Drink.keg'
        db.alter_column(u'core_drink', 'keg_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.PROTECT, to=orm['core.Keg']))

        # Changing field 'Drink.session'
        db.alter_column(u'core_drink', 'session_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.PROTECT, to=orm['core.DrinkingSession']))
        # Deleting field 'AuthenticationToken.site'
        db.delete_column(u'core_authenticationtoken', 'site_id')

        # Deleting field 'SessionStats.site'
        db.delete_column(u'core_sessionstats', 'site_id')

        # Deleting field 'ThermoSensor.site'
        db.delete_column(u'core_thermosensor', 'site_id')

        # Deleting field 'SystemStats.site'
        db.delete_column(u'core_systemstats', 'site_id')


        # Changing field 'UserProfile.mugshot'
        db.alter_column(u'core_userprofile', 'mugshot_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Picture'], null=True, on_delete=models.SET_NULL))
        # Deleting field 'Thermolog.site'
        db.delete_column(u'core_thermolog', 'site_id')


        # Changing field 'PourPicture.keg'
        db.alter_column(u'core_pourpicture', 'keg_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.SET_NULL, to=orm['core.Keg']))

        # Changing field 'SiteSettings.background_image'
        db.alter_column(u'core_sitesettings', 'background_image_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Picture'], null=True, on_delete=models.SET_NULL))

        # Changing field 'SiteSettings.guest_image'
        db.alter_column(u'core_sitesettings', 'guest_image_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.SET_NULL, to=orm['core.Picture']))

        # Changing field 'SessionChunk.keg'
        db.alter_column(u'core_sessionchunk', 'keg_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.PROTECT, to=orm['core.Keg']))
        # Deleting field 'UserSessionChunk.site'
        db.delete_column(u'core_usersessionchunk', 'site_id')

        # Deleting field 'KegSessionChunk.site'
        db.delete_column(u'core_kegsessionchunk', 'site_id')


    def backwards(self, orm):
        # Removing unique constraint on 'UserStats', fields ['user']
        db.delete_unique(u'core_userstats', ['user_id'])

        # Adding field 'SystemEvent.site'
        db.add_column(u'core_systemevent', 'site',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='events', to=orm['core.KegbotSite']),
                      keep_default=False)

        # Adding field 'Keg.site'
        db.add_column(u'core_keg', 'site',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='kegs', to=orm['core.KegbotSite']),
                      keep_default=False)


        # Changing field 'Keg.type'
        db.alter_column(u'core_keg', 'type_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.BeerType']))

        # Changing field 'Keg.size'
        db.alter_column(u'core_keg', 'size_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.KegSize']))
        # Adding field 'KegStats.site'
        db.add_column(u'core_kegstats', 'site',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['core.KegbotSite']),
                      keep_default=False)

        # Adding field 'UserStats.site'
        db.add_column(u'core_userstats', 'site',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['core.KegbotSite']),
                      keep_default=False)

        # Adding unique constraint on 'UserStats', fields ['site', 'user']
        db.create_unique(u'core_userstats', ['site_id', 'user_id'])


        # Changing field 'BeerType.image'
        db.alter_column(u'core_beertype', 'image_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['core.Picture']))
        # Adding field 'Picture.site'
        db.add_column(u'core_picture', 'site',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='pictures', null=True, to=orm['core.KegbotSite'], blank=True),
                      keep_default=False)


        # Changing field 'Brewer.image'
        db.alter_column(u'core_brewer', 'image_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['core.Picture']))
        # Adding field 'KegTap.site'
        db.add_column(u'core_kegtap', 'site',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='taps', to=orm['core.KegbotSite']),
                      keep_default=False)


        # Changing field 'KegTap.temperature_sensor'
        db.alter_column(u'core_kegtap', 'temperature_sensor_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.ThermoSensor'], null=True))
        # Adding field 'DrinkingSession.site'
        db.add_column(u'core_drinkingsession', 'site',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='sessions', to=orm['core.KegbotSite']),
                      keep_default=False)

        # Adding field 'Drink.site'
        db.add_column(u'core_drink', 'site',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='drinks', to=orm['core.KegbotSite']),
                      keep_default=False)


        # Changing field 'Drink.keg'
        db.alter_column(u'core_drink', 'keg_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['core.Keg']))

        # Changing field 'Drink.session'
        db.alter_column(u'core_drink', 'session_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['core.DrinkingSession']))
        # Adding field 'AuthenticationToken.site'
        db.add_column(u'core_authenticationtoken', 'site',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='tokens', to=orm['core.KegbotSite']),
                      keep_default=False)

        # Adding field 'SessionStats.site'
        db.add_column(u'core_sessionstats', 'site',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['core.KegbotSite']),
                      keep_default=False)

        # Adding field 'ThermoSensor.site'
        db.add_column(u'core_thermosensor', 'site',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='thermosensors', to=orm['core.KegbotSite']),
                      keep_default=False)

        # Adding field 'SystemStats.site'
        db.add_column(u'core_systemstats', 'site',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['core.KegbotSite']),
                      keep_default=False)


        # Changing field 'UserProfile.mugshot'
        db.alter_column(u'core_userprofile', 'mugshot_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Picture'], null=True))
        # Adding field 'Thermolog.site'
        db.add_column(u'core_thermolog', 'site',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='thermologs', to=orm['core.KegbotSite']),
                      keep_default=False)


        # Changing field 'PourPicture.keg'
        db.alter_column(u'core_pourpicture', 'keg_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['core.Keg']))

        # Changing field 'SiteSettings.background_image'
        db.alter_column(u'core_sitesettings', 'background_image_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Picture'], null=True))

        # Changing field 'SiteSettings.guest_image'
        db.alter_column(u'core_sitesettings', 'guest_image_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['core.Picture']))

        # Changing field 'SessionChunk.keg'
        db.alter_column(u'core_sessionchunk', 'keg_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['core.Keg']))
        # Adding field 'UserSessionChunk.site'
        db.add_column(u'core_usersessionchunk', 'site',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='user_chunks', to=orm['core.KegbotSite']),
                      keep_default=False)

        # Adding field 'KegSessionChunk.site'
        db.add_column(u'core_kegsessionchunk', 'site',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='keg_chunks', to=orm['core.KegbotSite']),
                      keep_default=False)


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'core.apikey': {
            'Meta': {'object_name': 'ApiKey'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '127'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        },
        u'core.authenticationtoken': {
            'Meta': {'unique_together': "(('auth_device', 'token_value'),)", 'object_name': 'AuthenticationToken'},
            'auth_device': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'created_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'expire_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nice_name': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'pin': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'token_value': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'tokens'", 'null': 'True', 'to': u"orm['auth.User']"})
        },
        u'core.beerstyle': {
            'Meta': {'object_name': 'BeerStyle'},
            'added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'beerdb_id': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'edited': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'core.beertype': {
            'Meta': {'object_name': 'BeerType'},
            'abv': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'beerdb_id': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'brewer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Brewer']"}),
            'calories_oz': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'carbs_oz': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'edited': ('django.db.models.fields.DateTimeField', [], {}),
            'edition': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'beer_types'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['core.Picture']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'original_gravity': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'specific_gravity': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'style': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.BeerStyle']"}),
            'untappd_beer_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'core.brewer': {
            'Meta': {'object_name': 'Brewer'},
            'added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'beerdb_id': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'country': ('pykeg.core.fields.CountryField', [], {'default': "'USA'", 'max_length': '3'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'edited': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'beer_brewers'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['core.Picture']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'origin_city': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'origin_state': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'production': ('django.db.models.fields.CharField', [], {'default': "'commercial'", 'max_length': '128'}),
            'url': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        u'core.drink': {
            'Meta': {'ordering': "('-time',)", 'object_name': 'Drink'},
            'duration': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keg': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'drinks'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['core.Keg']"}),
            'session': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'drinks'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['core.DrinkingSession']"}),
            'shout': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'valid'", 'max_length': '128'}),
            'tick_time_series': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'ticks': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'time': ('django.db.models.fields.DateTimeField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'drinks'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'volume_ml': ('django.db.models.fields.FloatField', [], {})
        },
        u'core.drinkingsession': {
            'Meta': {'ordering': "('-start_time',)", 'object_name': 'DrinkingSession'},
            'end_time': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {}),
            'volume_ml': ('django.db.models.fields.FloatField', [], {'default': '0'})
        },
        u'core.keg': {
            'Meta': {'object_name': 'Keg'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'end_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'origcost': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'size': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.KegSize']", 'on_delete': 'models.PROTECT'}),
            'spilled_ml': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.BeerType']", 'on_delete': 'models.PROTECT'})
        },
        u'core.kegbotsite': {
            'Meta': {'object_name': 'KegbotSite'},
            'epoch': ('django.db.models.fields.PositiveIntegerField', [], {'default': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_setup': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'default'", 'unique': 'True', 'max_length': '64'}),
            'serial_number': ('django.db.models.fields.TextField', [], {'default': "''", 'max_length': '128', 'blank': 'True'})
        },
        u'core.kegsessionchunk': {
            'Meta': {'ordering': "('-start_time',)", 'unique_together': "(('session', 'keg'),)", 'object_name': 'KegSessionChunk'},
            'end_time': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keg': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'keg_session_chunks'", 'null': 'True', 'to': u"orm['core.Keg']"}),
            'session': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'keg_chunks'", 'to': u"orm['core.DrinkingSession']"}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {}),
            'volume_ml': ('django.db.models.fields.FloatField', [], {'default': '0'})
        },
        u'core.kegsize': {
            'Meta': {'object_name': 'KegSize'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'volume_ml': ('django.db.models.fields.FloatField', [], {})
        },
        u'core.kegstats': {
            'Meta': {'object_name': 'KegStats'},
            'completed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keg': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'stats'", 'unique': 'True', 'to': u"orm['core.Keg']"}),
            'stats': ('pykeg.core.jsonfield.JSONField', [], {'default': "'{}'"}),
            'time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
        },
        u'core.kegtap': {
            'Meta': {'object_name': 'KegTap'},
            'current_keg': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'current_tap'", 'unique': 'True', 'null': 'True', 'to': u"orm['core.Keg']"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_tick_delta': ('django.db.models.fields.PositiveIntegerField', [], {'default': '100'}),
            'meter_name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'ml_per_tick': ('django.db.models.fields.FloatField', [], {'default': '0.45454545454545453'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'relay_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'temperature_sensor': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.ThermoSensor']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'})
        },
        u'core.picture': {
            'Meta': {'object_name': 'Picture'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
        },
        u'core.pourpicture': {
            'Meta': {'object_name': 'PourPicture'},
            'caption': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'drink': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'pictures'", 'null': 'True', 'to': u"orm['core.Drink']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keg': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'pictures'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['core.Keg']"}),
            'picture': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Picture']"}),
            'session': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'pictures'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['core.DrinkingSession']"}),
            'time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        u'core.sessionchunk': {
            'Meta': {'ordering': "('-start_time',)", 'unique_together': "(('session', 'user', 'keg'),)", 'object_name': 'SessionChunk'},
            'end_time': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keg': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'session_chunks'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['core.Keg']"}),
            'session': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'chunks'", 'to': u"orm['core.DrinkingSession']"}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'session_chunks'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'volume_ml': ('django.db.models.fields.FloatField', [], {'default': '0'})
        },
        u'core.sessionstats': {
            'Meta': {'object_name': 'SessionStats'},
            'completed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'session': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'stats'", 'unique': 'True', 'to': u"orm['core.DrinkingSession']"}),
            'stats': ('pykeg.core.jsonfield.JSONField', [], {'default': "'{}'"}),
            'time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
        },
        u'core.sitesettings': {
            'Meta': {'object_name': 'SiteSettings'},
            'allowed_hosts': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'background_image': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Picture']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'default_user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'event_web_hook': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'google_analytics_id': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'guest_image': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'guest_images'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['core.Picture']"}),
            'guest_name': ('django.db.models.fields.CharField', [], {'default': "'guest'", 'max_length': '63'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'privacy': ('django.db.models.fields.CharField', [], {'default': "'public'", 'max_length': '63'}),
            'registration_allowed': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'registration_confirmation': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'session_timeout_minutes': ('django.db.models.fields.PositiveIntegerField', [], {'default': '180'}),
            'site': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'settings'", 'unique': 'True', 'to': u"orm['core.KegbotSite']"}),
            'temperature_display_units': ('django.db.models.fields.CharField', [], {'default': "'f'", 'max_length': '64'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'volume_display_units': ('django.db.models.fields.CharField', [], {'default': "'imperial'", 'max_length': '64'})
        },
        u'core.systemevent': {
            'Meta': {'ordering': "('-id',)", 'object_name': 'SystemEvent'},
            'drink': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'events'", 'null': 'True', 'to': u"orm['core.Drink']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keg': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'events'", 'null': 'True', 'to': u"orm['core.Keg']"}),
            'kind': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'session': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'events'", 'null': 'True', 'to': u"orm['core.DrinkingSession']"}),
            'time': ('django.db.models.fields.DateTimeField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'events'", 'null': 'True', 'to': u"orm['auth.User']"})
        },
        u'core.systemstats': {
            'Meta': {'object_name': 'SystemStats'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'stats': ('pykeg.core.jsonfield.JSONField', [], {'default': "'{}'"}),
            'time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
        },
        u'core.thermolog': {
            'Meta': {'ordering': "('-time',)", 'object_name': 'Thermolog'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sensor': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.ThermoSensor']"}),
            'temp': ('django.db.models.fields.FloatField', [], {}),
            'time': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'core.thermosensor': {
            'Meta': {'object_name': 'ThermoSensor'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nice_name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'raw_name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'core.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mugshot': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Picture']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        },
        u'core.usersessionchunk': {
            'Meta': {'ordering': "('-start_time',)", 'unique_together': "(('session', 'user'),)", 'object_name': 'UserSessionChunk'},
            'end_time': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'session': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user_chunks'", 'to': u"orm['core.DrinkingSession']"}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'user_session_chunks'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'volume_ml': ('django.db.models.fields.FloatField', [], {'default': '0'})
        },
        u'core.userstats': {
            'Meta': {'object_name': 'UserStats'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'stats': ('pykeg.core.jsonfield.JSONField', [], {'default': "'{}'"}),
            'time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'stats'", 'unique': 'True', 'null': 'True', 'to': u"orm['auth.User']"})
        }
    }

    complete_apps = ['core']