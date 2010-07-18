# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'UserLabel'
        db.delete_table('core_userlabel')

        # Removing M2M table for field labels on 'UserProfile'
        db.delete_table('core_userprofile_labels')


    def backwards(self, orm):
        
        # Adding model 'UserLabel'
        db.create_table('core_userlabel', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('labelname', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal('core', ['UserLabel'])

        # Adding M2M table for field labels on 'UserProfile'
        db.create_table('core_userprofile_labels', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('userprofile', models.ForeignKey(orm['core.userprofile'], null=False)),
            ('userlabel', models.ForeignKey(orm['core.userlabel'], null=False))
        ))
        db.create_unique('core_userprofile_labels', ['userprofile_id', 'userlabel_id'])


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
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
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'beerdb.beerimage': {
            'Meta': {'object_name': 'BeerImage'},
            'added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'edited': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '36', 'primary_key': 'True'}),
            'num_views': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'original_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'revision': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'beerdb.beerstyle': {
            'Meta': {'object_name': 'BeerStyle'},
            'added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'edited': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '36', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'revision': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'beerdb.beertype': {
            'Meta': {'object_name': 'BeerType'},
            'abv': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'brewer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['beerdb.Brewer']"}),
            'calories_oz': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'carbs_oz': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'edited': ('django.db.models.fields.DateTimeField', [], {}),
            'edition': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '36', 'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'beers'", 'null': 'True', 'to': "orm['beerdb.BeerImage']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'original_gravity': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'revision': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'specific_gravity': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'style': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['beerdb.BeerStyle']"})
        },
        'beerdb.brewer': {
            'Meta': {'object_name': 'Brewer'},
            'added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'country': ('pykeg.core.fields.CountryField', [], {'default': "'USA'", 'max_length': '3'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'edited': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '36', 'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'brewers'", 'null': 'True', 'to': "orm['beerdb.BeerImage']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'origin_city': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'origin_state': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'production': ('django.db.models.fields.CharField', [], {'default': "'commercial'", 'max_length': '128'}),
            'revision': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'url': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'core.authenticationtoken': {
            'Meta': {'unique_together': "(('auth_device', 'token_value'),)", 'object_name': 'AuthenticationToken'},
            'auth_device': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'expires': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pin': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'token_value': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'core.bac': {
            'Meta': {'object_name': 'BAC'},
            'bac': ('django.db.models.fields.FloatField', [], {}),
            'drink': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Drink']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rectime': ('django.db.models.fields.DateTimeField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'core.config': {
            'Meta': {'object_name': 'Config'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'value': ('django.db.models.fields.TextField', [], {})
        },
        'core.drink': {
            'Meta': {'object_name': 'Drink'},
            'endtime': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keg': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Keg']", 'null': 'True', 'blank': 'True'}),
            'starttime': ('django.db.models.fields.DateTimeField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'valid'", 'max_length': '128'}),
            'ticks': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'volume_ml': ('django.db.models.fields.FloatField', [], {})
        },
        'core.drinkingsession': {
            'Meta': {'object_name': 'DrinkingSession'},
            'drinks': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.Drink']", 'symmetrical': 'False'}),
            'endtime': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kegs': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.Keg']", 'symmetrical': 'False'}),
            'starttime': ('django.db.models.fields.DateTimeField', [], {}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False'})
        },
        'core.drinkingsessionuserpart': {
            'Meta': {'unique_together': "(('session', 'user'),)", 'object_name': 'DrinkingSessionUserPart'},
            'endtime': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'session': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user_parts'", 'to': "orm['core.DrinkingSession']"}),
            'starttime': ('django.db.models.fields.DateTimeField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'session_parts'", 'to': "orm['auth.User']"}),
            'volume_ml': ('django.db.models.fields.FloatField', [], {'default': '0'})
        },
        'core.keg': {
            'Meta': {'object_name': 'Keg'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'enddate': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'origcost': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'size': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.KegSize']"}),
            'startdate': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['beerdb.BeerType']"})
        },
        'core.kegsize': {
            'Meta': {'object_name': 'KegSize'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'volume_ml': ('django.db.models.fields.FloatField', [], {})
        },
        'core.kegstats': {
            'Meta': {'object_name': 'KegStats'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keg': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'stats'", 'unique': 'True', 'to': "orm['core.Keg']"}),
            'revision': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'stats': ('pykeg.core.jsonfield.JSONField', [], {'default': "'{}'"})
        },
        'core.kegtap': {
            'Meta': {'object_name': 'KegTap'},
            'current_keg': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Keg']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_tick_delta': ('django.db.models.fields.PositiveIntegerField', [], {'default': '100'}),
            'meter_name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'ml_per_tick': ('django.db.models.fields.FloatField', [], {'default': '0.45454545454545453'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'temperature_sensor': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.ThermoSensor']", 'null': 'True', 'blank': 'True'})
        },
        'core.relaylog': {
            'Meta': {'object_name': 'RelayLog'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'time': ('django.db.models.fields.DateTimeField', [], {})
        },
        'core.thermolog': {
            'Meta': {'object_name': 'Thermolog'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sensor': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.ThermoSensor']"}),
            'temp': ('django.db.models.fields.FloatField', [], {}),
            'time': ('django.db.models.fields.DateTimeField', [], {})
        },
        'core.thermosensor': {
            'Meta': {'object_name': 'ThermoSensor'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nice_name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'raw_name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'core.thermosummarylog': {
            'Meta': {'object_name': 'ThermoSummaryLog'},
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_temp': ('django.db.models.fields.FloatField', [], {}),
            'mean_temp': ('django.db.models.fields.FloatField', [], {}),
            'min_temp': ('django.db.models.fields.FloatField', [], {}),
            'num_readings': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'period': ('django.db.models.fields.CharField', [], {'default': "'daily'", 'max_length': '64'}),
            'sensor': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.ThermoSensor']"})
        },
        'core.userpicture': {
            'Meta': {'object_name': 'UserPicture'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'core.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mugshot': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.UserPicture']", 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'}),
            'weight': ('django.db.models.fields.FloatField', [], {})
        },
        'core.userstats': {
            'Meta': {'object_name': 'UserStats'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'revision': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'stats': ('pykeg.core.jsonfield.JSONField', [], {'default': "'{}'"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'stats'", 'unique': 'True', 'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['core']
