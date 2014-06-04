# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'User'
        db.create_table(u'core_user', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('last_login', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('is_superuser', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('username', self.gf('django.db.models.fields.CharField')(unique=True, max_length=30)),
            ('display_name', self.gf('django.db.models.fields.CharField')(default='', max_length=127)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('is_staff', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('date_joined', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('mugshot', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='user_mugshot', null=True, on_delete=models.SET_NULL, to=orm['core.Picture'])),
            ('activation_key', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
        ))
        db.send_create_signal(u'core', ['User'])

        # Adding model 'Invitation'
        db.create_table(u'core_invitation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('invite_code', self.gf('django.db.models.fields.CharField')(default='496f2e0d-36c7-4690-a243-f4f324b3c829', unique=True, max_length=255)),
            ('for_email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('invited_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('expires_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 6, 5, 0, 0))),
            ('invited_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.User'], null=True, on_delete=models.SET_NULL)),
        ))
        db.send_create_signal(u'core', ['Invitation'])

        # Adding model 'KegbotSite'
        db.create_table(u'core_kegbotsite', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default='default', unique=True, max_length=64)),
            ('server_version', self.gf('django.db.models.fields.CharField')(max_length=64, null=True)),
            ('is_setup', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('registration_id', self.gf('django.db.models.fields.TextField')(default='', max_length=128, blank=True)),
            ('volume_display_units', self.gf('django.db.models.fields.CharField')(default='imperial', max_length=64)),
            ('temperature_display_units', self.gf('django.db.models.fields.CharField')(default='f', max_length=64)),
            ('title', self.gf('django.db.models.fields.CharField')(default='My Kegbot', max_length=64)),
            ('background_image', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Picture'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('google_analytics_id', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('session_timeout_minutes', self.gf('django.db.models.fields.PositiveIntegerField')(default=180)),
            ('privacy', self.gf('django.db.models.fields.CharField')(default='public', max_length=63)),
            ('registration_mode', self.gf('django.db.models.fields.CharField')(default='public', max_length=63)),
            ('timezone', self.gf('django.db.models.fields.CharField')(default='UTC', max_length=255)),
            ('check_for_updates', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'core', ['KegbotSite'])

        # Adding model 'Device'
        db.create_table(u'core_device', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default='Unknown Device', max_length=255)),
            ('created_time', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal(u'core', ['Device'])

        # Adding model 'ApiKey'
        db.create_table(u'core_apikey', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.User'], null=True, blank=True)),
            ('device', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Device'], null=True)),
            ('key', self.gf('django.db.models.fields.CharField')(default='3b59b5562ad9c0402f8e9565705a6949', unique=True, max_length=127)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('created_time', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal(u'core', ['ApiKey'])

        # Adding model 'BeverageProducer'
        db.create_table(u'core_beverageproducer', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('country', self.gf('pykeg.core.fields.CountryField')(default='USA', max_length=3)),
            ('origin_state', self.gf('django.db.models.fields.CharField')(default='', max_length=128, null=True, blank=True)),
            ('origin_city', self.gf('django.db.models.fields.CharField')(default='', max_length=128, null=True, blank=True)),
            ('is_homebrew', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('url', self.gf('django.db.models.fields.URLField')(default='', max_length=200, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(default='', null=True, blank=True)),
            ('picture', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Picture'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('beverage_backend', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('beverage_backend_id', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal(u'core', ['BeverageProducer'])

        # Adding model 'Beverage'
        db.create_table(u'core_beverage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('producer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.BeverageProducer'])),
            ('beverage_type', self.gf('django.db.models.fields.CharField')(default='beer', max_length=32)),
            ('style', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('picture', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Picture'], null=True, blank=True)),
            ('vintage_year', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('abv_percent', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('calories_per_ml', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('carbs_per_ml', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('original_gravity', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('specific_gravity', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('untappd_beer_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('beverage_backend', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('beverage_backend_id', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal(u'core', ['Beverage'])

        # Adding model 'KegTap'
        db.create_table(u'core_kegtap', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('current_keg', self.gf('django.db.models.fields.related.OneToOneField')(related_name='current_tap', null=True, on_delete=models.SET_NULL, to=orm['core.Keg'], blank=True, unique=True)),
            ('temperature_sensor', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.ThermoSensor'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('sort_order', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
        ))
        db.send_create_signal(u'core', ['KegTap'])

        # Adding model 'Controller'
        db.create_table(u'core_controller', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
            ('model_name', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('serial_number', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
        ))
        db.send_create_signal(u'core', ['Controller'])

        # Adding model 'FlowMeter'
        db.create_table(u'core_flowmeter', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('controller', self.gf('django.db.models.fields.related.ForeignKey')(related_name='meters', to=orm['core.Controller'])),
            ('port_name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('tap', self.gf('django.db.models.fields.related.OneToOneField')(blank=True, related_name='meter', unique=True, null=True, to=orm['core.KegTap'])),
            ('ticks_per_ml', self.gf('django.db.models.fields.FloatField')(default=5.4)),
        ))
        db.send_create_signal(u'core', ['FlowMeter'])

        # Adding unique constraint on 'FlowMeter', fields ['controller', 'port_name']
        db.create_unique(u'core_flowmeter', ['controller_id', 'port_name'])

        # Adding model 'FlowToggle'
        db.create_table(u'core_flowtoggle', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('controller', self.gf('django.db.models.fields.related.ForeignKey')(related_name='toggles', to=orm['core.Controller'])),
            ('port_name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('tap', self.gf('django.db.models.fields.related.OneToOneField')(blank=True, related_name='toggle', unique=True, null=True, to=orm['core.KegTap'])),
        ))
        db.send_create_signal(u'core', ['FlowToggle'])

        # Adding unique constraint on 'FlowToggle', fields ['controller', 'port_name']
        db.create_unique(u'core_flowtoggle', ['controller_id', 'port_name'])

        # Adding model 'Keg'
        db.create_table(u'core_keg', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Beverage'], on_delete=models.PROTECT)),
            ('keg_type', self.gf('django.db.models.fields.CharField')(default='half-barrel', max_length=32)),
            ('served_volume_ml', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('full_volume_ml', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('end_time', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('online', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('finished', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('spilled_ml', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'core', ['Keg'])

        # Adding model 'Drink'
        db.create_table(u'core_drink', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ticks', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('volume_ml', self.gf('django.db.models.fields.FloatField')()),
            ('time', self.gf('django.db.models.fields.DateTimeField')()),
            ('duration', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='drinks', to=orm['core.User'])),
            ('keg', self.gf('django.db.models.fields.related.ForeignKey')(related_name='drinks', on_delete=models.PROTECT, to=orm['core.Keg'])),
            ('session', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='drinks', null=True, on_delete=models.PROTECT, to=orm['core.DrinkingSession'])),
            ('shout', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('tick_time_series', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('picture', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.Picture'], unique=True, null=True, on_delete=models.SET_NULL, blank=True)),
        ))
        db.send_create_signal(u'core', ['Drink'])

        # Adding model 'AuthenticationToken'
        db.create_table(u'core_authenticationtoken', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('auth_device', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('token_value', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('nice_name', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('pin', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='tokens', null=True, to=orm['core.User'])),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('created_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('expire_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'core', ['AuthenticationToken'])

        # Adding unique constraint on 'AuthenticationToken', fields ['auth_device', 'token_value']
        db.create_unique(u'core_authenticationtoken', ['auth_device', 'token_value'])

        # Adding model 'DrinkingSession'
        db.create_table(u'core_drinkingsession', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('end_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('volume_ml', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
        ))
        db.send_create_signal(u'core', ['DrinkingSession'])

        # Adding model 'ThermoSensor'
        db.create_table(u'core_thermosensor', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('raw_name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('nice_name', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal(u'core', ['ThermoSensor'])

        # Adding model 'Thermolog'
        db.create_table(u'core_thermolog', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sensor', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.ThermoSensor'])),
            ('temp', self.gf('django.db.models.fields.FloatField')()),
            ('time', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'core', ['Thermolog'])

        # Adding model 'Stats'
        db.create_table(u'core_stats', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('time', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('stats', self.gf('pykeg.core.jsonfield.JSONField')()),
            ('drink', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Drink'])),
            ('is_first', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='stats', null=True, to=orm['core.User'])),
            ('keg', self.gf('django.db.models.fields.related.ForeignKey')(related_name='stats', null=True, to=orm['core.Keg'])),
            ('session', self.gf('django.db.models.fields.related.ForeignKey')(related_name='stats', null=True, to=orm['core.DrinkingSession'])),
        ))
        db.send_create_signal(u'core', ['Stats'])

        # Adding unique constraint on 'Stats', fields ['drink', 'user', 'keg', 'session']
        db.create_unique(u'core_stats', ['drink_id', 'user_id', 'keg_id', 'session_id'])

        # Adding model 'SystemEvent'
        db.create_table(u'core_systemevent', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('kind', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('time', self.gf('django.db.models.fields.DateTimeField')()),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='events', null=True, to=orm['core.User'])),
            ('drink', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='events', null=True, to=orm['core.Drink'])),
            ('keg', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='events', null=True, to=orm['core.Keg'])),
            ('session', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='events', null=True, to=orm['core.DrinkingSession'])),
        ))
        db.send_create_signal(u'core', ['SystemEvent'])

        # Adding model 'Picture'
        db.create_table(u'core_picture', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('time', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('caption', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='pictures', null=True, to=orm['core.User'])),
            ('keg', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='pictures', null=True, on_delete=models.SET_NULL, to=orm['core.Keg'])),
            ('session', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='pictures', null=True, on_delete=models.SET_NULL, to=orm['core.DrinkingSession'])),
        ))
        db.send_create_signal(u'core', ['Picture'])

        # Adding model 'NotificationSettings'
        db.create_table(u'core_notificationsettings', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.User'])),
            ('backend', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('keg_tapped', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('session_started', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('keg_volume_low', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('keg_ended', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'core', ['NotificationSettings'])

        # Adding unique constraint on 'NotificationSettings', fields ['user', 'backend']
        db.create_unique(u'core_notificationsettings', ['user_id', 'backend'])

        # Adding model 'PluginData'
        db.create_table(u'core_plugindata', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('plugin_name', self.gf('django.db.models.fields.CharField')(max_length=127)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=127)),
            ('value', self.gf('pykeg.core.jsonfield.JSONField')()),
        ))
        db.send_create_signal(u'core', ['PluginData'])

        # Adding unique constraint on 'PluginData', fields ['plugin_name', 'key']
        db.create_unique(u'core_plugindata', ['plugin_name', 'key'])


    def backwards(self, orm):
        # Removing unique constraint on 'PluginData', fields ['plugin_name', 'key']
        db.delete_unique(u'core_plugindata', ['plugin_name', 'key'])

        # Removing unique constraint on 'NotificationSettings', fields ['user', 'backend']
        db.delete_unique(u'core_notificationsettings', ['user_id', 'backend'])

        # Removing unique constraint on 'Stats', fields ['drink', 'user', 'keg', 'session']
        db.delete_unique(u'core_stats', ['drink_id', 'user_id', 'keg_id', 'session_id'])

        # Removing unique constraint on 'AuthenticationToken', fields ['auth_device', 'token_value']
        db.delete_unique(u'core_authenticationtoken', ['auth_device', 'token_value'])

        # Removing unique constraint on 'FlowToggle', fields ['controller', 'port_name']
        db.delete_unique(u'core_flowtoggle', ['controller_id', 'port_name'])

        # Removing unique constraint on 'FlowMeter', fields ['controller', 'port_name']
        db.delete_unique(u'core_flowmeter', ['controller_id', 'port_name'])

        # Deleting model 'User'
        db.delete_table(u'core_user')

        # Deleting model 'Invitation'
        db.delete_table(u'core_invitation')

        # Deleting model 'KegbotSite'
        db.delete_table(u'core_kegbotsite')

        # Deleting model 'Device'
        db.delete_table(u'core_device')

        # Deleting model 'ApiKey'
        db.delete_table(u'core_apikey')

        # Deleting model 'BeverageProducer'
        db.delete_table(u'core_beverageproducer')

        # Deleting model 'Beverage'
        db.delete_table(u'core_beverage')

        # Deleting model 'KegTap'
        db.delete_table(u'core_kegtap')

        # Deleting model 'Controller'
        db.delete_table(u'core_controller')

        # Deleting model 'FlowMeter'
        db.delete_table(u'core_flowmeter')

        # Deleting model 'FlowToggle'
        db.delete_table(u'core_flowtoggle')

        # Deleting model 'Keg'
        db.delete_table(u'core_keg')

        # Deleting model 'Drink'
        db.delete_table(u'core_drink')

        # Deleting model 'AuthenticationToken'
        db.delete_table(u'core_authenticationtoken')

        # Deleting model 'DrinkingSession'
        db.delete_table(u'core_drinkingsession')

        # Deleting model 'ThermoSensor'
        db.delete_table(u'core_thermosensor')

        # Deleting model 'Thermolog'
        db.delete_table(u'core_thermolog')

        # Deleting model 'Stats'
        db.delete_table(u'core_stats')

        # Deleting model 'SystemEvent'
        db.delete_table(u'core_systemevent')

        # Deleting model 'Picture'
        db.delete_table(u'core_picture')

        # Deleting model 'NotificationSettings'
        db.delete_table(u'core_notificationsettings')

        # Deleting model 'PluginData'
        db.delete_table(u'core_plugindata')


    models = {
        u'core.apikey': {
            'Meta': {'object_name': 'ApiKey'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'created_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'device': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Device']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'default': "'541f07b2788b4e33f152d05c440f183c'", 'unique': 'True', 'max_length': '127'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.User']", 'null': 'True', 'blank': 'True'})
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
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'tokens'", 'null': 'True', 'to': u"orm['core.User']"})
        },
        u'core.beverage': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Beverage'},
            'abv_percent': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'beverage_backend': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'beverage_backend_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'beverage_type': ('django.db.models.fields.CharField', [], {'default': "'beer'", 'max_length': '32'}),
            'calories_per_ml': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'carbs_per_ml': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'original_gravity': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'picture': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Picture']", 'null': 'True', 'blank': 'True'}),
            'producer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.BeverageProducer']"}),
            'specific_gravity': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'style': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'untappd_beer_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'vintage_year': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'})
        },
        u'core.beverageproducer': {
            'Meta': {'ordering': "('name',)", 'object_name': 'BeverageProducer'},
            'beverage_backend': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'beverage_backend_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'country': ('pykeg.core.fields.CountryField', [], {'default': "'USA'", 'max_length': '3'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_homebrew': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'origin_city': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'origin_state': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'picture': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Picture']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        u'core.controller': {
            'Meta': {'object_name': 'Controller'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'serial_number': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'})
        },
        u'core.device': {
            'Meta': {'object_name': 'Device'},
            'created_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'Unknown Device'", 'max_length': '255'})
        },
        u'core.drink': {
            'Meta': {'ordering': "('-time',)", 'object_name': 'Drink'},
            'duration': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keg': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'drinks'", 'on_delete': 'models.PROTECT', 'to': u"orm['core.Keg']"}),
            'picture': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['core.Picture']", 'unique': 'True', 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'session': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'drinks'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['core.DrinkingSession']"}),
            'shout': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'tick_time_series': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'ticks': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'time': ('django.db.models.fields.DateTimeField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'drinks'", 'to': u"orm['core.User']"}),
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
        u'core.flowmeter': {
            'Meta': {'unique_together': "(('controller', 'port_name'),)", 'object_name': 'FlowMeter'},
            'controller': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'meters'", 'to': u"orm['core.Controller']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'port_name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'tap': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'meter'", 'unique': 'True', 'null': 'True', 'to': u"orm['core.KegTap']"}),
            'ticks_per_ml': ('django.db.models.fields.FloatField', [], {'default': '5.4'})
        },
        u'core.flowtoggle': {
            'Meta': {'unique_together': "(('controller', 'port_name'),)", 'object_name': 'FlowToggle'},
            'controller': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'toggles'", 'to': u"orm['core.Controller']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'port_name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'tap': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'toggle'", 'unique': 'True', 'null': 'True', 'to': u"orm['core.KegTap']"})
        },
        u'core.invitation': {
            'Meta': {'object_name': 'Invitation'},
            'expires_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 6, 5, 0, 0)'}),
            'for_email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invite_code': ('django.db.models.fields.CharField', [], {'default': "'82db659b-2873-4eab-96fb-256561188e79'", 'unique': 'True', 'max_length': '255'}),
            'invited_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.User']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'invited_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        u'core.keg': {
            'Meta': {'object_name': 'Keg'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'end_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'finished': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'full_volume_ml': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keg_type': ('django.db.models.fields.CharField', [], {'default': "'half-barrel'", 'max_length': '32'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'online': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'served_volume_ml': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'spilled_ml': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Beverage']", 'on_delete': 'models.PROTECT'})
        },
        u'core.kegbotsite': {
            'Meta': {'object_name': 'KegbotSite'},
            'background_image': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Picture']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'check_for_updates': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'google_analytics_id': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_setup': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'default'", 'unique': 'True', 'max_length': '64'}),
            'privacy': ('django.db.models.fields.CharField', [], {'default': "'public'", 'max_length': '63'}),
            'registration_id': ('django.db.models.fields.TextField', [], {'default': "''", 'max_length': '128', 'blank': 'True'}),
            'registration_mode': ('django.db.models.fields.CharField', [], {'default': "'public'", 'max_length': '63'}),
            'server_version': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True'}),
            'session_timeout_minutes': ('django.db.models.fields.PositiveIntegerField', [], {'default': '180'}),
            'temperature_display_units': ('django.db.models.fields.CharField', [], {'default': "'f'", 'max_length': '64'}),
            'timezone': ('django.db.models.fields.CharField', [], {'default': "'UTC'", 'max_length': '255'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "'My Kegbot'", 'max_length': '64'}),
            'volume_display_units': ('django.db.models.fields.CharField', [], {'default': "'imperial'", 'max_length': '64'})
        },
        u'core.kegtap': {
            'Meta': {'ordering': "('sort_order', 'id')", 'object_name': 'KegTap'},
            'current_keg': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'current_tap'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['core.Keg']", 'blank': 'True', 'unique': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'sort_order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'temperature_sensor': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.ThermoSensor']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'})
        },
        u'core.notificationsettings': {
            'Meta': {'unique_together': "(('user', 'backend'),)", 'object_name': 'NotificationSettings'},
            'backend': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keg_ended': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'keg_tapped': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'keg_volume_low': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'session_started': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.User']"})
        },
        u'core.picture': {
            'Meta': {'object_name': 'Picture'},
            'caption': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'keg': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'pictures'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['core.Keg']"}),
            'session': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'pictures'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['core.DrinkingSession']"}),
            'time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'pictures'", 'null': 'True', 'to': u"orm['core.User']"})
        },
        u'core.plugindata': {
            'Meta': {'unique_together': "(('plugin_name', 'key'),)", 'object_name': 'PluginData'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '127'}),
            'plugin_name': ('django.db.models.fields.CharField', [], {'max_length': '127'}),
            'value': ('pykeg.core.jsonfield.JSONField', [], {})
        },
        u'core.stats': {
            'Meta': {'unique_together': "(('drink', 'user', 'keg', 'session'),)", 'object_name': 'Stats'},
            'drink': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Drink']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_first': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'keg': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'stats'", 'null': 'True', 'to': u"orm['core.Keg']"}),
            'session': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'stats'", 'null': 'True', 'to': u"orm['core.DrinkingSession']"}),
            'stats': ('pykeg.core.jsonfield.JSONField', [], {}),
            'time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'stats'", 'null': 'True', 'to': u"orm['core.User']"})
        },
        u'core.systemevent': {
            'Meta': {'ordering': "('-id',)", 'object_name': 'SystemEvent'},
            'drink': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'events'", 'null': 'True', 'to': u"orm['core.Drink']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keg': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'events'", 'null': 'True', 'to': u"orm['core.Keg']"}),
            'kind': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'session': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'events'", 'null': 'True', 'to': u"orm['core.DrinkingSession']"}),
            'time': ('django.db.models.fields.DateTimeField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'events'", 'null': 'True', 'to': u"orm['core.User']"})
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
        u'core.user': {
            'Meta': {'object_name': 'User'},
            'activation_key': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'display_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '127'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'mugshot': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'user_mugshot'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['core.Picture']"}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        }
    }

    complete_apps = ['core']