# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='kegbotsite',
            name='enable_sensing',
            field=models.BooleanField(default=True, help_text=b'Enable and show features related to volume sensing.'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='kegbotsite',
            name='enable_users',
            field=models.BooleanField(default=True, help_text=b'Enable user pour tracking.'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='keg',
            name='description',
            field=models.TextField(help_text=b'User-visible description of the Keg.', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.RenameField(
            model_name='kegtap',
            old_name='description',
            new_name='notes',
        ),
        migrations.AlterField(
            model_name='kegtap',
            name='notes',
            field=models.TextField(help_text=b'Private notes about this tap.', null=True, blank=True),
            preserve_default=True,
        ),
    ]
