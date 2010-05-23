# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

import uuid

class Migration(DataMigration):
    
    def forwards(self, orm):
        brewer_map = {}
        # Brewers
        for brewer in orm.Brewer.objects.all():
          new = orm.models['beerdb.brewer']()
          new.name = brewer.name
          new.country = 'USA' # can't migrate from free-form string, assume USA
          new.origin_state = brewer.origin_state
          new.origin_city = brewer.origin_city
          if brewer.distribution == 'homebrew':
            new.production = 'homebrew'
          else:
            new.production = 'commercial'
          new.url = brewer.url
          new.description = brewer.comment
          new.id = uuid.uuid4()
          new.edited = datetime.datetime.now()
          new.save()
          brewer_map[brewer.id] = new.id

        # Styles
        style_map = {}
        for style in orm.BeerStyle.objects.all():
          new = orm.models['beerdb.beerstyle']()
          new.name = style.name
          new.id = uuid.uuid4()
          new.edited = datetime.datetime.now()
          new.save()
          style_map[style.id] = new.id

        # BeerTypes
        type_map = {}
        for t in orm.BeerType.objects.all():
          new = orm.models['beerdb.beertype']()
          new.name = t.name
          new.brewer_id = brewer_map[t.brewer.id]
          new.style_id = style_map[t.style.id]
          if t.calories_oz:
            new.calories_oz = t.calories_oz
          if t.carbs_oz:
            new.carbs_oz = t.carbs_oz
          if t.abv:
            new.abv = t.abv
          new.id = uuid.uuid4()
          new.edited = datetime.datetime.now()
          new.save()
          type_map[t.id] = new

        # kegs
        for k in orm.Keg.objects.all():
          k.newtype = type_map[k.type.id]
          k.save()
          print k.newtype

    
    
    def backwards(self, orm):
        "Write your backwards methods here."
    
    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'})
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
        'core.beerstyle': {
            'Meta': {'object_name': 'BeerStyle'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'core.beertype': {
            'Meta': {'object_name': 'BeerType'},
            'abv': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'brewer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Brewer']"}),
            'calories_oz': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'carbs_oz': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'style': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.BeerStyle']"})
        },
        'core.brewer': {
            'Meta': {'object_name': 'Brewer'},
            'comment': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'distribution': ('django.db.models.fields.CharField', [], {'default': "'unknown'", 'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'origin_city': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'origin_country': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128'}),
            'origin_state': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128'}),
            'url': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '200', 'null': 'True', 'blank': 'True'})
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
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'volume_ml': ('django.db.models.fields.FloatField', [], {})
        },
        'core.drinkingsession': {
            'Meta': {'object_name': 'DrinkingSession'},
            'drinks': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.Drink']"}),
            'endtime': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kegs': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.Keg']"}),
            'starttime': ('django.db.models.fields.DateTimeField', [], {}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']"})
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
            'newtype': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['beerdb.BeerType']", 'null': 'True', 'blank': 'True'}),
            'origcost': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'size': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.KegSize']"}),
            'startdate': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.BeerType']"})
        },
        'core.kegsize': {
            'Meta': {'object_name': 'KegSize'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'volume_ml': ('django.db.models.fields.FloatField', [], {})
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
        'core.userlabel': {
            'Meta': {'object_name': 'UserLabel'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'labelname': ('django.db.models.fields.CharField', [], {'max_length': '128'})
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
            'labels': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.UserLabel']"}),
            'mugshot': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.UserPicture']", 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'}),
            'weight': ('django.db.models.fields.FloatField', [], {})
        }
    }
    
    complete_apps = ['core']
