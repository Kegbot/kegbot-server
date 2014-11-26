# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def set_initial_status(apps, schema_editor):
    Keg = apps.get_model("core", "Keg")
    for keg in Keg.objects.all():
        if keg.finished:
            keg.status = 'finished'
        else:
            keg.status = 'available'
        keg.save()

    KegTap = apps.get_model("core", "KegTap")
    for tap in KegTap.objects.all():
        if tap.current_keg:
            keg = tap.current_keg
            keg.status = 'on_tap'
            keg.save()


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
        migrations.AddField(
            model_name='keg',
            name='status',
            field=models.CharField(default=b'available', help_text=b'Current keg state.', max_length=32, choices=[(b'available', b'Available'), (b'on_tap', b'On tap'), (b'finished', b'Finished')]),
            preserve_default=True,
        ),
        migrations.RunPython(set_initial_status),
        migrations.RemoveField(
            model_name='keg',
            name='finished',
        ),
        migrations.RemoveField(
            model_name='keg',
            name='online',
        ),
    ]
