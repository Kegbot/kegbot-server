"""Unittests for pykeg.backup.backup"""

import difflib
import os
import sys
import shutil
import tempfile
import unittest

from pykeg.core import defaults
from pykeg.core import models

from django.core.files.storage import FileSystemStorage
from django.test import TransactionTestCase

from . import backup
from pykeg.core.testutils import make_datetime
from pykeg.core.util import get_version

from pykeg.util import kbjson


def run(cmd, args=[]):
    cmdname = cmd.__module__.split(".")[-1]
    cmd.run_from_argv([sys.argv[0], cmdname] + args)


@unittest.skip("backup tests failing")
class BackupTestCase(TransactionTestCase):
    def setUp(self):
        self.temp_storage_location = tempfile.mkdtemp(dir=os.environ.get("DJANGO_TEST_TEMP_DIR"))
        self.storage = FileSystemStorage(location=self.temp_storage_location)
        self.now = make_datetime(2014, 4, 1)

    def tearDown(self):
        shutil.rmtree(self.temp_storage_location)

    def assertMetadata(self, backup_dir, when=None, site_name="My Kegbot", num_media_files=0):
        when = when or self.now

        backup.verify_backup_directory(backup_dir)
        metadata_file = os.path.join(backup_dir, backup.METADATA_FILENAME)
        metadata_json = kbjson.loads(open(metadata_file).read())

        self.assertEqual(when, metadata_json[backup.META_CREATED_TIME])
        self.assertEqual(site_name, metadata_json[backup.META_SERVER_NAME])
        self.assertEqual(num_media_files, metadata_json[backup.META_NUM_MEDIA_FILES])
        self.assertEqual(get_version(), metadata_json[backup.META_SERVER_VERSION])

    def test_create_backup_tree_empty_site(self):
        # Create a backup of an empty system.
        backup_dir = backup.create_backup_tree(self.now, storage=self.storage)

        try:
            self.assertMetadata(backup_dir, site_name="kegbot")
        finally:
            shutil.rmtree(backup_dir)

    def test_create_backup_tree_with_defaults(self):
        defaults.set_defaults(set_is_setup=True)

        site = models.KegbotSite.get()
        site.title = "Kegbot Test 2"
        site.save()

        backup_dir = backup.create_backup_tree(self.now, storage=self.storage)

        try:
            self.assertMetadata(backup_dir, site_name="Kegbot Test 2")
        finally:
            shutil.rmtree(backup_dir)

    def test_restore_needs_erase(self):
        defaults.set_defaults(set_is_setup=True)
        backup_dir = backup.create_backup_tree(self.now, storage=self.storage)

        try:
            # Restore must fail when something is already installed.
            self.assertRaises(
                backup.AlreadyInstalledError, backup.restore_from_directory, backup_dir
            )

            # Erase and restore.
            backup.erase(self.storage)
            backup.restore_from_directory(backup_dir, self.storage)
        finally:
            shutil.rmtree(backup_dir)

    def test_backup_contents_same(self):
        defaults.set_defaults(set_is_setup=True)
        backup_dir = backup.create_backup_tree(self.now, storage=self.storage)

        try:
            # Verify recursive_diff works with no diffs.
            self.recursive_diff(backup_dir, backup_dir)

            second_backup_dir = backup.create_backup_tree(self.now, storage=self.storage)
            try:
                self.recursive_diff(backup_dir, second_backup_dir)
            finally:
                shutil.rmtree(second_backup_dir)
        finally:
            shutil.rmtree(backup_dir)

    def recursive_diff(self, dir1, dir2):
        dir1_files = set()
        dir2_files = set()

        for dirname, subdirs, files in os.walk(dir1):
            for filename in files:
                full_path = os.path.join(dirname, filename)
                rel_path = os.path.relpath(full_path, dir1)
                dir1_files.add(rel_path)

        for dirname, subdirs, files in os.walk(dir2):
            for filename in files:
                full_path = os.path.join(dirname, filename)
                rel_path = os.path.relpath(full_path, dir2)
                dir2_files.add(rel_path)

        self.assertEqual(dir1_files, dir2_files)

        for relfile in dir1_files:
            f1_full = os.path.join(dir1, relfile)
            f2_full = os.path.join(dir2, relfile)
            f1 = open(f1_full).read()
            f2 = open(f2_full).read()
            if f1 != f2:
                message = 'Files not equal: "{}" and "{}" differ.'.format(f1_full, f2_full)
                message += "\n" + "".join(difflib.ndiff(f1.splitlines(True), f2.splitlines(True)))
                self.fail(message)
