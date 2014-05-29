# Copyright 2014 Bevbot LLC, All Rights Reserved
#
# This file is part of the Pykeg package of the Kegbot project.
# For more information on Pykeg or Kegbot, see http://kegbot.org/
#
# Pykeg is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# Pykeg is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pykeg.  If not, see <http://www.gnu.org/licenses/>.

"""Unittests for pykeg.core.backup"""

import difflib
import os
import sys
import shutil
import tempfile

from pykeg.core import defaults
from pykeg.core import models

from django.core import serializers
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.test import TransactionTestCase

from . import backup
from .testutils import make_datetime
from pykeg.core.util import get_version
from south.management.commands import migrate

from kegbot.util import kbjson

EXPECTED_SAVED_TABLES = [
    u'core_apikey',
    u'core_authenticationtoken',
    u'core_beverage',
    u'core_beverageproducer',
    u'core_controller',
    u'core_device',
    u'core_drink',
    u'core_drinkingsession',
    u'core_flowmeter',
    u'core_flowtoggle',
    u'core_invitation',
    u'core_keg',
    u'core_kegbotsite',
    u'core_kegtap',
    u'core_notificationsettings',
    u'core_picture',
    u'core_plugindata',
    u'core_stats',
    u'core_systemevent',
    u'core_thermolog',
    u'core_thermosensor',
    u'core_user',
    u'south_migrationhistory',
]


def run(cmd, args=[]):
    cmdname = cmd.__module__.split('.')[-1]
    cmd.run_from_argv([sys.argv[0], cmdname] + args)


class BackupTestCase(TransactionTestCase):
    def setUp(self):
        self.temp_storage_location = tempfile.mkdtemp(dir=os.environ.get('DJANGO_TEST_TEMP_DIR'))
        self.storage = FileSystemStorage(location=self.temp_storage_location)
        self.now = make_datetime(2014, 4, 1)

        # Backup requires a fully-populated migrations table, so inject
        # them if the unittest runner isn't actually doing them.
        if not settings.SOUTH_TESTS_MIGRATE:
            run(migrate.Command(), args=['-v', '0', '--all', '--fake'])

    def tearDown(self):
        shutil.rmtree(self.temp_storage_location)

    def load_table(self, backup_dir, table_name):
        filename = os.path.join(backup_dir, backup.TABLES_DIRNAME, table_name + '.json')
        data = open(filename, 'r').read()
        return list(serializers.deserialize('json', data))

    def assertMetadata(self, backup_dir, when=None, site_name='My Kegbot',
            num_tables=len(EXPECTED_SAVED_TABLES), num_media_files=0):
        when = when or self.now

        backup.verify_backup_directory(backup_dir)
        metadata_file = os.path.join(backup_dir, backup.METADATA_FILENAME)
        metadata_json = kbjson.loads(open(metadata_file).read())

        self.assertEqual(when, metadata_json[backup.META_CREATED_TIME])
        self.assertEquals(site_name, metadata_json[backup.META_SERVER_NAME])
        self.assertEquals(num_tables, metadata_json[backup.META_NUM_TABLES])
        self.assertEquals(num_media_files, metadata_json[backup.META_NUM_MEDIA_FILES])
        self.assertEquals(get_version(), metadata_json[backup.META_SERVER_VERSION])

    def test_create_backup_tree_empty_site(self):
        # Create a backup of an empty system.
        backup_dir = backup.create_backup_tree(self.now, storage=self.storage)

        try:
            self.assertMetadata(backup_dir)

            for table_name in EXPECTED_SAVED_TABLES:
                if table_name != 'south_migrationhistory':
                    objects = self.load_table(backup_dir, table_name)
                    self.assertEqual(0, len(objects))
        finally:
            shutil.rmtree(backup_dir)

    def test_create_backup_tree_with_defaults(self):
        defaults.set_defaults(set_is_setup=True)

        site = models.KegbotSite.get()
        site.title = 'Kegbot Test 2'
        site.save()

        backup_dir = backup.create_backup_tree(self.now, storage=self.storage)

        try:
            self.assertMetadata(backup_dir, site_name='Kegbot Test 2')

            sites = self.load_table(backup_dir, 'core_kegbotsite')
            self.assertEqual(1, len(sites))
            self.assertEqual('Kegbot Test 2', sites[0].object.title)

            users = self.load_table(backup_dir, 'core_user')
            self.assertEqual(1, len(users))
            self.assertEqual('guest', users[0].object.username)

            taps = self.load_table(backup_dir, 'core_kegtap')
            self.assertEqual(1, len(taps))
            self.assertEqual('Main Tap', taps[0].object.name)
        finally:
            shutil.rmtree(backup_dir)

    def test_restore_needs_erase(self):
        defaults.set_defaults(set_is_setup=True)
        backup_dir = backup.create_backup_tree(self.now, storage=self.storage)

        try:
            # Restore must fail when something is already installed.
            self.assertRaises(backup.AlreadyInstalledError, backup.restore_from_directory,
                    backup_dir)

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
                message += '\n' + ''.join(difflib.ndiff(f1.splitlines(True), f2.splitlines(True)))
                self.fail(message)
