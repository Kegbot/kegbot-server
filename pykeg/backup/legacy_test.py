"""Tests for legacy (format-1) backup restore."""

import json
import os
import shutil
import tempfile
import unittest

from django.apps import apps
from django.core import serializers
from django.core.files.storage import FileSystemStorage
from django.core.management import call_command
from django.test import TransactionTestCase

from pykeg.backup import backup, legacy
from pykeg.core import defaults, models
from pykeg.core.util import get_version

METER_NAME = "kegboard.flow0"
FAKE_BEER_NAME = "Testy Beer"
FAKE_BREWER_NAME = "Unittest Brewery"
FAKE_BEER_STYLE = "Test-Driven Pale Ale"

MEDIA_CONTENTS = b"\xff\xd8\xff fake jpeg bytes"


class TransformTablesTestCase(unittest.TestCase):
    def test_keg_status(self):
        tables = {
            "core_kegtap": [{"pk": 1, "model": "core.kegtap", "fields": {"current_keg": 2}}],
            "core_keg": [
                {"pk": 1, "model": "core.keg", "fields": {"finished": True, "online": False}},
                {"pk": 2, "model": "core.keg", "fields": {"finished": False, "online": True}},
                {"pk": 3, "model": "core.keg", "fields": {"finished": False, "online": False}},
            ],
        }
        objects = legacy.transform_tables(tables)
        statuses = {o["pk"]: o["fields"]["status"] for o in objects if o["model"] == "core.keg"}
        self.assertEqual({1: "finished", 2: "on_tap", 3: "available"}, statuses)
        for o in objects:
            self.assertNotIn("finished", o["fields"])
            self.assertNotIn("online", o["fields"])

    def test_kegtap_description_renamed(self):
        tables = {
            "core_kegtap": [
                {"pk": 1, "model": "core.kegtap", "fields": {"description": "spare tap"}}
            ]
        }
        (tap,) = legacy.transform_tables(tables)
        self.assertEqual("spare tap", tap["fields"]["notes"])
        self.assertNotIn("description", tap["fields"])

    def test_site_and_session_fields(self):
        tables = {
            "core_kegbotsite": [
                {
                    "pk": 1,
                    "model": "core.kegbotsite",
                    "fields": {"check_for_updates": True, "timezone": "US/Pacific"},
                }
            ],
            "core_drinkingsession": [
                {"pk": 1, "model": "core.drinkingsession", "fields": {}},
            ],
            "south_migrationhistory": [
                {"pk": 1, "model": "south.migrationhistory", "fields": {}},
            ],
        }
        objects = legacy.transform_tables(tables)
        by_model = {o["model"]: o for o in objects}
        self.assertNotIn("south.migrationhistory", by_model)
        self.assertNotIn("check_for_updates", by_model["core.kegbotsite"]["fields"])
        self.assertEqual("US/Pacific", by_model["core.drinkingsession"]["fields"]["timezone"])


class LegacyRestoreTestCase(TransactionTestCase):
    def setUp(self):
        defaults.set_defaults(set_is_setup=True, create_controller=True)
        models.Keg.start_keg(
            METER_NAME,
            beverage_name=FAKE_BEER_NAME,
            beverage_type="beer",
            producer_name=FAKE_BREWER_NAME,
            style_name=FAKE_BEER_STYLE,
        )
        models.Drink.record_drink(METER_NAME, ticks=2200, volume_ml=1000)
        models.Drink.record_drink(METER_NAME, ticks=1100, volume_ml=500)

        self.backup_dir = tempfile.mkdtemp()
        self.media_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.backup_dir)
        self.addCleanup(shutil.rmtree, self.media_dir)

    def build_format1_backup(self):
        """Serializes current site data devolved to v1.1 fixture shape."""
        tables = {}
        for model in apps.get_app_config("core").get_models():
            rows = json.loads(serializers.serialize("json", model.objects.all()))
            if rows:
                tables[model._meta.db_table] = rows

        for row in tables["core_kegbotsite"]:
            row["fields"]["check_for_updates"] = True
            row["fields"]["server_version"] = "1.1"
        for row in tables["core_kegtap"]:
            row["fields"]["description"] = row["fields"].pop("notes", "")
        for row in tables["core_keg"]:
            status = row["fields"].pop("status")
            row["fields"]["finished"] = status == "finished"
            row["fields"]["online"] = status == "on_tap"
        for row in tables.get("core_drinkingsession", []):
            row["fields"].pop("timezone", None)

        tables_dir = os.path.join(self.backup_dir, legacy.TABLES_DIRNAME)
        os.makedirs(tables_dir)
        for name, rows in tables.items():
            with open(os.path.join(tables_dir, f"{name}.json"), "w") as f:
                json.dump(rows, f)

        with open(os.path.join(self.backup_dir, "metadata.json"), "w") as f:
            json.dump({"backup_format": 1, "server_version": "1.1.0"}, f)

        pics_dir = os.path.join(self.backup_dir, "media", "pics")
        os.makedirs(pics_dir)
        with open(os.path.join(pics_dir, "test.jpg"), "wb") as f:
            f.write(MEDIA_CONTENTS)

        return tables

    def test_restore(self):
        tables = self.build_format1_backup()
        expected_counts = {name: len(rows) for name, rows in tables.items()}

        call_command("flush", interactive=False, verbosity=0)
        self.assertFalse(models.KegbotSite.objects.exists())

        storage = FileSystemStorage(location=self.media_dir)
        backup.restore_from_directory(self.backup_dir, storage=storage)

        site = models.KegbotSite.get()
        self.assertEqual(get_version(), site.server_version)

        for model in apps.get_app_config("core").get_models():
            expected = expected_counts.get(model._meta.db_table, 0)
            self.assertEqual(
                expected, model.objects.count(), f"count mismatch for {model._meta.db_table}"
            )

        keg = models.Keg.objects.get()
        self.assertEqual(models.Keg.STATUS_ON_TAP, keg.status)
        self.assertEqual(2, models.Drink.objects.count())

        with storage.open("pics/test.jpg") as f:
            self.assertEqual(MEDIA_CONTENTS, f.read())

        # Sequences realigned: creating new records must not collide.
        models.Drink.record_drink(METER_NAME, ticks=1100, volume_ml=500)
        self.assertEqual(3, models.Drink.objects.count())

    def test_restore_requires_empty_site(self):
        self.build_format1_backup()
        storage = FileSystemStorage(location=self.media_dir)
        with self.assertRaises(backup.AlreadyInstalledError):
            backup.restore_from_directory(self.backup_dir, storage=storage)
