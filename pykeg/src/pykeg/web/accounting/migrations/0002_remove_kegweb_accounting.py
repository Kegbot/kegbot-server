# -*- coding: latin-1 -*-

from south.db import db
from django.db import models
from pykeg.web.accounting.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Deleting model 'drinkcharge'
        db.delete_table('accounting_drinkcharge')
        
        # Deleting model 'misccharge'
        db.delete_table('accounting_misccharge')
        
        # Deleting model 'billstatement'
        db.delete_table('accounting_billstatement')
        
        # Deleting model 'payment'
        db.delete_table('accounting_payment')
        
    
    
    def backwards(self, orm):
        
        # Adding model 'drinkcharge'
        db.create_table('accounting_drinkcharge', (
            ('base_funds', orm['accounting.payment:base_funds']),
            ('user', orm['accounting.payment:user']),
            ('statement', orm['accounting.payment:statement']),
            ('handling_funds', orm['accounting.payment:handling_funds']),
            ('ext_funds', orm['accounting.payment:ext_funds']),
            ('drink', orm['accounting.payment:drink']),
            ('id', orm['accounting.payment:id']),
            ('tax_funds', orm['accounting.payment:tax_funds']),
        ))
        db.send_create_signal('accounting', ['drinkcharge'])
        
        # Adding model 'misccharge'
        db.create_table('accounting_misccharge', (
            ('long_desc', orm['accounting.payment:long_desc']),
            ('base_funds', orm['accounting.payment:base_funds']),
            ('user', orm['accounting.payment:user']),
            ('statement', orm['accounting.payment:statement']),
            ('handling_funds', orm['accounting.payment:handling_funds']),
            ('ext_funds', orm['accounting.payment:ext_funds']),
            ('short_desc', orm['accounting.payment:short_desc']),
            ('id', orm['accounting.payment:id']),
            ('tax_funds', orm['accounting.payment:tax_funds']),
        ))
        db.send_create_signal('accounting', ['misccharge'])
        
        # Adding model 'billstatement'
        db.create_table('accounting_billstatement', (
            ('long_desc', orm['accounting.payment:long_desc']),
            ('statement_id', orm['accounting.payment:statement_id']),
            ('statement_date', orm['accounting.payment:statement_date']),
            ('short_desc', orm['accounting.payment:short_desc']),
            ('user', orm['accounting.payment:user']),
            ('id', orm['accounting.payment:id']),
        ))
        db.send_create_signal('accounting', ['billstatement'])
        
        # Adding model 'payment'
        db.create_table('accounting_payment', (
            ('base_funds', orm['accounting.payment:base_funds']),
            ('payment_status', orm['accounting.payment:payment_status']),
            ('tax_funds', orm['accounting.payment:tax_funds']),
            ('handling_funds', orm['accounting.payment:handling_funds']),
            ('user', orm['accounting.payment:user']),
            ('id', orm['accounting.payment:id']),
            ('payment_date', orm['accounting.payment:payment_date']),
            ('source_user', orm['accounting.payment:source_user']),
            ('statement', orm['accounting.payment:statement']),
            ('ext_funds', orm['accounting.payment:ext_funds']),
            ('status_message', orm['accounting.payment:status_message']),
            ('payment_funds_source', orm['accounting.payment:payment_funds_source']),
            ('transaction_id', orm['accounting.payment:transaction_id']),
        ))
        db.send_create_signal('accounting', ['payment'])
        
    
    
    models = {
        
    }
    
    complete_apps = ['accounting']
