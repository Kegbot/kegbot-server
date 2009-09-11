
from south.db import db
from django.db import models
from pykeg.contrib.twitter.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'DrinkRemark'
        db.create_table('twitter_drinkremark', (
            ('id', orm['twitter.DrinkRemark:id']),
            ('drink_class', orm['twitter.DrinkRemark:drink_class']),
            ('remark', orm['twitter.DrinkRemark:remark']),
        ))
        db.send_create_signal('twitter', ['DrinkRemark'])
        
        # Adding model 'DrinkClassification'
        db.create_table('twitter_drinkclassification', (
            ('id', orm['twitter.DrinkClassification:id']),
            ('name', orm['twitter.DrinkClassification:name']),
            ('minimum_volume', orm['twitter.DrinkClassification:minimum_volume']),
        ))
        db.send_create_signal('twitter', ['DrinkClassification'])
        
        # Adding model 'TweetLog'
        db.create_table('twitter_tweetlog', (
            ('id', orm['twitter.TweetLog:id']),
            ('twitter_id', orm['twitter.TweetLog:twitter_id']),
            ('tweet', orm['twitter.TweetLog:tweet']),
        ))
        db.send_create_signal('twitter', ['TweetLog'])
        
        # Adding model 'UserTwitterLink'
        db.create_table('twitter_usertwitterlink', (
            ('user_profile', orm['twitter.UserTwitterLink:user_profile']),
            ('twitter_name', orm['twitter.UserTwitterLink:twitter_name']),
            ('validated', orm['twitter.UserTwitterLink:validated']),
        ))
        db.send_create_signal('twitter', ['UserTwitterLink'])
        
        # Adding model 'DrinkTweetLog'
        db.create_table('twitter_drinktweetlog', (
            ('id', orm['twitter.DrinkTweetLog:id']),
            ('tweet_log', orm['twitter.DrinkTweetLog:tweet_log']),
            ('drink', orm['twitter.DrinkTweetLog:drink']),
        ))
        db.send_create_signal('twitter', ['DrinkTweetLog'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'DrinkRemark'
        db.delete_table('twitter_drinkremark')
        
        # Deleting model 'DrinkClassification'
        db.delete_table('twitter_drinkclassification')
        
        # Deleting model 'TweetLog'
        db.delete_table('twitter_tweetlog')
        
        # Deleting model 'UserTwitterLink'
        db.delete_table('twitter_usertwitterlink')
        
        # Deleting model 'DrinkTweetLog'
        db.delete_table('twitter_drinktweetlog')
        
    
    
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
        'core.userlabel': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'labelname': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'core.userprofile': {
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'labels': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.UserLabel']"}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'}),
            'weight': ('django.db.models.fields.FloatField', [], {})
        },
        'twitter.drinkclassification': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'minimum_volume': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'twitter.drinkremark': {
            'drink_class': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['twitter.DrinkClassification']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'remark': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'twitter.drinktweetlog': {
            'drink': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Drink']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tweet_log': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['twitter.TweetLog']"})
        },
        'twitter.tweetlog': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tweet': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'twitter_id': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'twitter.usertwitterlink': {
            'twitter_name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'user_profile': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.UserProfile']", 'unique': 'True', 'primary_key': 'True'}),
            'validated': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'})
        }
    }
    
    complete_apps = ['twitter']
