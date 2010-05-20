# -*- coding: latin-1 -*-

from south.db import db
from django.db import models
from pykeg.web.accounting.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'DrinkCharge'
        db.create_table('accounting_drinkcharge', (
            ('id', orm['accounting.DrinkCharge:id']),
            ('user', orm['accounting.DrinkCharge:user']),
            ('base_funds', orm['accounting.DrinkCharge:base_funds']),
            ('ext_funds', orm['accounting.DrinkCharge:ext_funds']),
            ('tax_funds', orm['accounting.DrinkCharge:tax_funds']),
            ('handling_funds', orm['accounting.DrinkCharge:handling_funds']),
            ('statement', orm['accounting.DrinkCharge:statement']),
            ('drink', orm['accounting.DrinkCharge:drink']),
        ))
        db.send_create_signal('accounting', ['DrinkCharge'])
        
        # Adding model 'MiscCharge'
        db.create_table('accounting_misccharge', (
            ('id', orm['accounting.MiscCharge:id']),
            ('user', orm['accounting.MiscCharge:user']),
            ('base_funds', orm['accounting.MiscCharge:base_funds']),
            ('ext_funds', orm['accounting.MiscCharge:ext_funds']),
            ('tax_funds', orm['accounting.MiscCharge:tax_funds']),
            ('handling_funds', orm['accounting.MiscCharge:handling_funds']),
            ('statement', orm['accounting.MiscCharge:statement']),
            ('short_desc', orm['accounting.MiscCharge:short_desc']),
            ('long_desc', orm['accounting.MiscCharge:long_desc']),
        ))
        db.send_create_signal('accounting', ['MiscCharge'])
        
        # Adding model 'BillStatement'
        db.create_table('accounting_billstatement', (
            ('id', orm['accounting.BillStatement:id']),
            ('user', orm['accounting.BillStatement:user']),
            ('statement_date', orm['accounting.BillStatement:statement_date']),
            ('statement_id', orm['accounting.BillStatement:statement_id']),
            ('short_desc', orm['accounting.BillStatement:short_desc']),
            ('long_desc', orm['accounting.BillStatement:long_desc']),
        ))
        db.send_create_signal('accounting', ['BillStatement'])
        
        # Adding model 'Payment'
        db.create_table('accounting_payment', (
            ('id', orm['accounting.Payment:id']),
            ('user', orm['accounting.Payment:user']),
            ('base_funds', orm['accounting.Payment:base_funds']),
            ('ext_funds', orm['accounting.Payment:ext_funds']),
            ('tax_funds', orm['accounting.Payment:tax_funds']),
            ('handling_funds', orm['accounting.Payment:handling_funds']),
            ('source_user', orm['accounting.Payment:source_user']),
            ('statement', orm['accounting.Payment:statement']),
            ('payment_date', orm['accounting.Payment:payment_date']),
            ('payment_funds_source', orm['accounting.Payment:payment_funds_source']),
            ('transaction_id', orm['accounting.Payment:transaction_id']),
            ('payment_status', orm['accounting.Payment:payment_status']),
            ('status_message', orm['accounting.Payment:status_message']),
        ))
        db.send_create_signal('accounting', ['Payment'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'DrinkCharge'
        db.delete_table('accounting_drinkcharge')
        
        # Deleting model 'MiscCharge'
        db.delete_table('accounting_misccharge')
        
        # Deleting model 'BillStatement'
        db.delete_table('accounting_billstatement')
        
        # Deleting model 'Payment'
        db.delete_table('accounting_payment')
        
    
    
    models = {
        'accounting.billstatement': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'long_desc': ('django.db.models.fields.TextField', [], {}),
            'short_desc': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'statement_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'statement_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'accounting.drinkcharge': {
            'base_funds': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'drink': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Drink']"}),
            'ext_funds': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'handling_funds': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'statement': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'drink_charges'", 'null': 'True', 'to': "orm['accounting.BillStatement']"}),
            'tax_funds': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'accounting.misccharge': {
            'base_funds': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'ext_funds': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'handling_funds': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'long_desc': ('django.db.models.fields.TextField', [], {}),
            'short_desc': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'statement': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'misc_charges'", 'null': 'True', 'to': "orm['accounting.BillStatement']"}),
            'tax_funds': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'accounting.payment': {
            'base_funds': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'ext_funds': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'handling_funds': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'payment_date': ('django.db.models.fields.DateTimeField', [], {}),
            'payment_funds_source': ('django.db.models.fields.CharField', [], {'default': "'cash'", 'max_length': '128'}),
            'payment_status': ('django.db.models.fields.CharField', [], {'default': "'complete'", 'max_length': '128'}),
            'source_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'outgoing_payments'", 'to': "orm['auth.User']"}),
            'statement': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounting.BillStatement']", 'null': 'True', 'blank': 'True'}),
            'status_message': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'tax_funds': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'transaction_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
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
        }
    }
    
    complete_apps = ['accounting']
