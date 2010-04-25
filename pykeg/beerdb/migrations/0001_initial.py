# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'Brewer'
        db.create_table('beerdb_brewer', (
            ('edited', self.gf('django.db.models.fields.DateTimeField')()),
            ('added', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('url', self.gf('django.db.models.fields.URLField')(default='', max_length=200, null=True, blank=True)),
            ('country', self.gf('pykeg.core.fields.CountryField')(default='USA', max_length=3)),
            ('description', self.gf('django.db.models.fields.TextField')(default='', null=True, blank=True)),
            ('production', self.gf('django.db.models.fields.CharField')(default='commercial', max_length=128)),
            ('origin_city', self.gf('django.db.models.fields.CharField')(default='', max_length=128, null=True, blank=True)),
            ('origin_state', self.gf('django.db.models.fields.CharField')(default='', max_length=128, null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.CharField')(max_length=36, primary_key=True)),
            ('revision', self.gf('django.db.models.fields.IntegerField')(default=1)),
        ))
        db.send_create_signal('beerdb', ['Brewer'])

        # Adding model 'BeerStyle'
        db.create_table('beerdb_beerstyle', (
            ('edited', self.gf('django.db.models.fields.DateTimeField')()),
            ('added', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('id', self.gf('django.db.models.fields.CharField')(max_length=36, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('revision', self.gf('django.db.models.fields.IntegerField')(default=1)),
        ))
        db.send_create_signal('beerdb', ['BeerStyle'])

        # Adding model 'BeerType'
        db.create_table('beerdb_beertype', (
            ('edited', self.gf('django.db.models.fields.DateTimeField')()),
            ('style', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['beerdb.BeerStyle'])),
            ('added', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('brewer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['beerdb.Brewer'])),
            ('carbs_oz', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('edition', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('calories_oz', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('abv', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('specific_gravity', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('original_gravity', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.CharField')(max_length=36, primary_key=True)),
            ('revision', self.gf('django.db.models.fields.IntegerField')(default=1)),
        ))
        db.send_create_signal('beerdb', ['BeerType'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'Brewer'
        db.delete_table('beerdb_brewer')

        # Deleting model 'BeerStyle'
        db.delete_table('beerdb_beerstyle')

        # Deleting model 'BeerType'
        db.delete_table('beerdb_beertype')
    
    
    models = {
        'beerdb.beerstyle': {
            'Meta': {'object_name': 'BeerStyle'},
            'added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'edited': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '36', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'revision': ('django.db.models.fields.IntegerField', [], {'default': '1'})
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
            'revision': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
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
            'revision': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'url': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '200', 'null': 'True', 'blank': 'True'})
        }
    }
    
    complete_apps = ['beerdb']
