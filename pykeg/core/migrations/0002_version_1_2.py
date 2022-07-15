# -*- coding: utf-8 -*-

from django.db import models, migrations


def set_initial_status(apps, schema_editor):
    Keg = apps.get_model("core", "Keg")
    for keg in Keg.objects.all():
        if keg.finished:
            keg.status = "finished"
        else:
            keg.status = "available"
        keg.save()

    KegTap = apps.get_model("core", "KegTap")
    for tap in KegTap.objects.all():
        if tap.current_keg:
            keg = tap.current_keg
            keg.status = "on_tap"
            keg.save()


def set_initial_time_zone(apps, schema_editor):
    KegbotSite = apps.get_model("core", "KegbotSite")
    try:
        site = KegbotSite.objects.get(name="default")
    except KegbotSite.DoesNotExist:
        return
    timezone = site.timezone

    DrinkingSession = apps.get_model("core", "DrinkingSession")
    for session in DrinkingSession.objects.all():
        session.timezone = timezone
        session.save()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="kegbotsite",
            name="enable_sensing",
            field=models.BooleanField(
                default=True, help_text="Enable and show features related to volume sensing."
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="kegbotsite",
            name="enable_users",
            field=models.BooleanField(default=True, help_text="Enable user pour tracking."),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="keg",
            name="description",
            field=models.TextField(
                help_text="User-visible description of the Keg.", null=True, blank=True
            ),
            preserve_default=True,
        ),
        migrations.RenameField(
            model_name="kegtap",
            old_name="description",
            new_name="notes",
        ),
        migrations.AlterField(
            model_name="kegtap",
            name="notes",
            field=models.TextField(
                help_text="Private notes about this tap.", null=True, blank=True
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="keg",
            name="status",
            field=models.CharField(
                default="available",
                help_text="Current keg state.",
                max_length=32,
                choices=[
                    ("available", "Available"),
                    ("on_tap", "On tap"),
                    ("finished", "Finished"),
                ],
            ),
            preserve_default=True,
        ),
        migrations.RunPython(set_initial_status),
        migrations.RemoveField(
            model_name="keg",
            name="finished",
        ),
        migrations.RemoveField(
            model_name="keg",
            name="online",
        ),
        migrations.AlterField(
            model_name="keg",
            name="full_volume_ml",
            field=models.FloatField(
                default=0,
                help_text="Full volume of this Keg; usually set automatically from keg_type.",
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="keg",
            name="keg_type",
            field=models.CharField(
                default="half-barrel",
                help_text="Keg container type, used to initialize keg's full volume",
                max_length=32,
                choices=[
                    ("corny-2_5-gal", "Corny Key (2.5 gal)"),
                    ("other", "Other"),
                    ("quarter", "Quarter Barrel (7.75 gal)"),
                    ("half-barrel", "Half Barrel (15.5 gal)"),
                    ("euro-half", "European Half Barrel (50 L)"),
                    ("corny", "Corny Keg (5 gal)"),
                    ("sixth", "Sixth Barrel (5.17 gal)"),
                    ("corny-3-gal", "Corny Keg (3.0 gal)"),
                    ("euro-30-liter", "European DIN (30 L)"),
                    ("euro", "European Full Barrel (100 L)"),
                ],
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="drinkingsession",
            name="timezone",
            field=models.CharField(default="UTC", max_length=256),
            preserve_default=True,
        ),
        migrations.RunPython(set_initial_time_zone),
    ]
