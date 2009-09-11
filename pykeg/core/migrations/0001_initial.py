# -*- coding: latin-1 -*-

from south.db import db
from django.db import models
from pykeg.core.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'DrinkingSessionGroup'
        db.create_table('core_drinkingsessiongroup', (
            ('id', orm['core.DrinkingSessionGroup:id']),
            ('starttime', orm['core.DrinkingSessionGroup:starttime']),
            ('endtime', orm['core.DrinkingSessionGroup:endtime']),
        ))
        db.send_create_signal('core', ['DrinkingSessionGroup'])
        
        # Adding model 'Config'
        db.create_table('core_config', (
            ('id', orm['core.Config:id']),
            ('key', orm['core.Config:key']),
            ('value', orm['core.Config:value']),
        ))
        db.send_create_signal('core', ['Config'])
        
        # Adding model 'BeerType'
        db.create_table('core_beertype', (
            ('id', orm['core.BeerType:id']),
            ('name', orm['core.BeerType:name']),
            ('brewer', orm['core.BeerType:brewer']),
            ('style', orm['core.BeerType:style']),
            ('calories_oz', orm['core.BeerType:calories_oz']),
            ('carbs_oz', orm['core.BeerType:carbs_oz']),
            ('abv', orm['core.BeerType:abv']),
        ))
        db.send_create_signal('core', ['BeerType'])
        
        # Adding model 'RelayLog'
        db.create_table('core_relaylog', (
            ('id', orm['core.RelayLog:id']),
            ('name', orm['core.RelayLog:name']),
            ('status', orm['core.RelayLog:status']),
            ('time', orm['core.RelayLog:time']),
        ))
        db.send_create_signal('core', ['RelayLog'])
        
        # Adding model 'UserPicture'
        db.create_table('core_userpicture', (
            ('id', orm['core.UserPicture:id']),
            ('user', orm['core.UserPicture:user']),
            ('image', orm['core.UserPicture:image']),
            ('active', orm['core.UserPicture:active']),
        ))
        db.send_create_signal('core', ['UserPicture'])
        
        # Adding model 'UserProfile'
        db.create_table('core_userprofile', (
            ('id', orm['core.UserProfile:id']),
            ('user', orm['core.UserProfile:user']),
            ('gender', orm['core.UserProfile:gender']),
            ('weight', orm['core.UserProfile:weight']),
        ))
        db.send_create_signal('core', ['UserProfile'])
        
        # Adding model 'Thermolog'
        db.create_table('core_thermolog', (
            ('id', orm['core.Thermolog:id']),
            ('name', orm['core.Thermolog:name']),
            ('temp', orm['core.Thermolog:temp']),
            ('time', orm['core.Thermolog:time']),
        ))
        db.send_create_signal('core', ['Thermolog'])
        
        # Adding model 'KegTap'
        db.create_table('core_kegtap', (
            ('id', orm['core.KegTap:id']),
            ('name', orm['core.KegTap:name']),
            ('meter_name', orm['core.KegTap:meter_name']),
            ('description', orm['core.KegTap:description']),
            ('current_keg', orm['core.KegTap:current_keg']),
        ))
        db.send_create_signal('core', ['KegTap'])
        
        # Adding model 'Token'
        db.create_table('core_token', (
            ('id', orm['core.Token:id']),
            ('user', orm['core.Token:user']),
            ('keyinfo', orm['core.Token:keyinfo']),
            ('created', orm['core.Token:created']),
        ))
        db.send_create_signal('core', ['Token'])
        
        # Adding model 'KegSize'
        db.create_table('core_kegsize', (
            ('id', orm['core.KegSize:id']),
            ('name', orm['core.KegSize:name']),
            ('volume', orm['core.KegSize:volume']),
        ))
        db.send_create_signal('core', ['KegSize'])
        
        # Adding model 'BAC'
        db.create_table('core_bac', (
            ('id', orm['core.BAC:id']),
            ('user', orm['core.BAC:user']),
            ('drink', orm['core.BAC:drink']),
            ('rectime', orm['core.BAC:rectime']),
            ('bac', orm['core.BAC:bac']),
        ))
        db.send_create_signal('core', ['BAC'])
        
        # Adding model 'Drink'
        db.create_table('core_drink', (
            ('id', orm['core.Drink:id']),
            ('ticks', orm['core.Drink:ticks']),
            ('volume', orm['core.Drink:volume']),
            ('starttime', orm['core.Drink:starttime']),
            ('endtime', orm['core.Drink:endtime']),
            ('user', orm['core.Drink:user']),
            ('keg', orm['core.Drink:keg']),
            ('status', orm['core.Drink:status']),
        ))
        db.send_create_signal('core', ['Drink'])
        
        # Adding model 'UserLabel'
        db.create_table('core_userlabel', (
            ('id', orm['core.UserLabel:id']),
            ('labelname', orm['core.UserLabel:labelname']),
        ))
        db.send_create_signal('core', ['UserLabel'])
        
        # Adding model 'UserDrinkingSession'
        db.create_table('core_userdrinkingsession', (
            ('id', orm['core.UserDrinkingSession:id']),
            ('user', orm['core.UserDrinkingSession:user']),
            ('starttime', orm['core.UserDrinkingSession:starttime']),
            ('endtime', orm['core.UserDrinkingSession:endtime']),
            ('group', orm['core.UserDrinkingSession:group']),
        ))
        db.send_create_signal('core', ['UserDrinkingSession'])
        
        # Adding model 'Brewer'
        db.create_table('core_brewer', (
            ('id', orm['core.Brewer:id']),
            ('name', orm['core.Brewer:name']),
            ('origin_country', orm['core.Brewer:origin_country']),
            ('origin_state', orm['core.Brewer:origin_state']),
            ('origin_city', orm['core.Brewer:origin_city']),
            ('distribution', orm['core.Brewer:distribution']),
            ('url', orm['core.Brewer:url']),
            ('comment', orm['core.Brewer:comment']),
        ))
        db.send_create_signal('core', ['Brewer'])
        
        # Adding model 'Keg'
        db.create_table('core_keg', (
            ('id', orm['core.Keg:id']),
            ('type', orm['core.Keg:type']),
            ('size', orm['core.Keg:size']),
            ('startdate', orm['core.Keg:startdate']),
            ('enddate', orm['core.Keg:enddate']),
            ('channel', orm['core.Keg:channel']),
            ('status', orm['core.Keg:status']),
            ('description', orm['core.Keg:description']),
            ('origcost', orm['core.Keg:origcost']),
        ))
        db.send_create_signal('core', ['Keg'])
        
        # Adding model 'UserDrinkingSessionAssignment'
        db.create_table('core_userdrinkingsessionassignment', (
            ('id', orm['core.UserDrinkingSessionAssignment:id']),
            ('drink', orm['core.UserDrinkingSessionAssignment:drink']),
            ('session', orm['core.UserDrinkingSessionAssignment:session']),
        ))
        db.send_create_signal('core', ['UserDrinkingSessionAssignment'])
        
        # Adding model 'BeerStyle'
        db.create_table('core_beerstyle', (
            ('id', orm['core.BeerStyle:id']),
            ('name', orm['core.BeerStyle:name']),
        ))
        db.send_create_signal('core', ['BeerStyle'])
        
        # Adding ManyToManyField 'UserProfile.labels'
        db.create_table('core_userprofile_labels', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('userprofile', models.ForeignKey(orm.UserProfile, null=False)),
            ('userlabel', models.ForeignKey(orm.UserLabel, null=False))
        ))
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'DrinkingSessionGroup'
        db.delete_table('core_drinkingsessiongroup')
        
        # Deleting model 'Config'
        db.delete_table('core_config')
        
        # Deleting model 'BeerType'
        db.delete_table('core_beertype')
        
        # Deleting model 'RelayLog'
        db.delete_table('core_relaylog')
        
        # Deleting model 'UserPicture'
        db.delete_table('core_userpicture')
        
        # Deleting model 'UserProfile'
        db.delete_table('core_userprofile')
        
        # Deleting model 'Thermolog'
        db.delete_table('core_thermolog')
        
        # Deleting model 'KegTap'
        db.delete_table('core_kegtap')
        
        # Deleting model 'Token'
        db.delete_table('core_token')
        
        # Deleting model 'KegSize'
        db.delete_table('core_kegsize')
        
        # Deleting model 'BAC'
        db.delete_table('core_bac')
        
        # Deleting model 'Drink'
        db.delete_table('core_drink')
        
        # Deleting model 'UserLabel'
        db.delete_table('core_userlabel')
        
        # Deleting model 'UserDrinkingSession'
        db.delete_table('core_userdrinkingsession')
        
        # Deleting model 'Brewer'
        db.delete_table('core_brewer')
        
        # Deleting model 'Keg'
        db.delete_table('core_keg')
        
        # Deleting model 'UserDrinkingSessionAssignment'
        db.delete_table('core_userdrinkingsessionassignment')
        
        # Deleting model 'BeerStyle'
        db.delete_table('core_beerstyle')
        
        # Dropping ManyToManyField 'UserProfile.labels'
        db.delete_table('core_userprofile_labels')
        
    
    
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
        'core.bac': {
            'bac': ('django.db.models.fields.FloatField', [], {}),
            'drink': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Drink']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rectime': ('django.db.models.fields.DateTimeField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'core.beerstyle': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'core.beertype': {
            'abv': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'brewer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Brewer']"}),
            'calories_oz': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'carbs_oz': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'style': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.BeerStyle']"})
        },
        'core.brewer': {
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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '256'}),
            'value': ('django.db.models.fields.TextField', [], {})
        },
        'core.drink': {
            'endtime': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keg': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Keg']", 'null': 'True', 'blank': 'True'}),
            'starttime': ('django.db.models.fields.DateTimeField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'valid'", 'max_length': '128'}),
            'ticks': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'volume': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'core.drinkingsessiongroup': {
            'endtime': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'starttime': ('django.db.models.fields.DateTimeField', [], {})
        },
        'core.keg': {
            'channel': ('django.db.models.fields.IntegerField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'enddate': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'origcost': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'size': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.KegSize']"}),
            'startdate': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.BeerType']"})
        },
        'core.kegsize': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'volume': ('django.db.models.fields.IntegerField', [], {})
        },
        'core.kegtap': {
            'current_keg': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Keg']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'meter_name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'core.relaylog': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'time': ('django.db.models.fields.DateTimeField', [], {})
        },
        'core.thermolog': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'temp': ('django.db.models.fields.FloatField', [], {}),
            'time': ('django.db.models.fields.DateTimeField', [], {})
        },
        'core.token': {
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keyinfo': ('django.db.models.fields.TextField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'core.userdrinkingsession': {
            'endtime': ('django.db.models.fields.DateTimeField', [], {}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.DrinkingSessionGroup']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'starttime': ('django.db.models.fields.DateTimeField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'core.userdrinkingsessionassignment': {
            'drink': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Drink']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'session': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.UserDrinkingSession']"})
        },
        'core.userlabel': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'labelname': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'core.userpicture': {
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'core.userprofile': {
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'labels': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.UserLabel']"}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'}),
            'weight': ('django.db.models.fields.FloatField', [], {})
        }
    }
    
    complete_apps = ['core']
