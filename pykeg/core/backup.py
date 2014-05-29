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

"""Site backup and restore functions.

Backup file format is a zipfile with following contents:
    backup-name/         - top-level directory
       metadata.json     - backup metadata
       media/            - site media
       tables/           - per-table json records

The zipfile name takes the form <backup-name>-<sha1sum>.zip.

`backup-name` takes the form <site-title>-<YYMMDD-HHMMSS>, where
`site-title` is the slugified version of the current Kegbot site's
title.

Note that both the zipfile name and the backup file dirname are
informational and may change in a future version.

metadata.json consists of backup-related metadata:
  'created_time': ISO8601 timestamp at backup create
  'num_media_files': number of files in the 'media/' folder
  'num_tables': number of files in the 'tables/' folder
  'server_version': server version at backup create time
  'server_name': server name at backup create time
"""


import hashlib
import logging
import os
import sys
import isodate
import tempfile
import shutil
import json
import zipfile

from pykeg.core import models
from pykeg.core.util import get_version
from kegbot.util import kbjson

from django.core.files.storage import default_storage
from django.core import serializers
from django.db import transaction
from django.db import connection
from django.db.models import get_models
from django.utils import timezone
from django.utils.text import slugify

from south import models as south_models

logger = logging.getLogger(__name__)

# Tables to ignore when creating backups.  These tables will still be erased
# if they exist, which is important in the case of django_session.
BACKUP_SKIPPED_TABLE_NAMES = [
    u'django_admin_log',
    u'django_session',
    u'django_content_type',
    u'auth_group',
    u'auth_permission'
]

# These tables are not wiped on erase (and thus may be non-empty on restore).
ERASE_SKIPPED_TABLE_NAMES = [
    u'south_migrationhistory',
]

# App names to back up, needed for south migration.
APP_NAMES = [
    u'core',
]

# Whitelist of directories to include from storage backend.
MEDIA_WHITELIST = [
    u'pics'
]

# Metadata key names.
METADATA_FILENAME = 'metadata.json'
META_CREATED_TIME = 'created_time'
META_NUM_MEDIA_FILES = 'num_media_files'
META_NUM_TABLES = 'num_tables'
META_SERVER_VERSION = 'server_version'
META_SERVER_NAME = 'server_name'
META_BACKUP_FORMAT = 'backup_format'

BACKUPS_DIRNAME = 'backups'
TABLES_DIRNAME = 'tables'

# Current protocol.
BACKUP_FORMAT = 1


class BackupError(IOError):
    """Base backup exception."""


class AlreadyInstalledError(BackupError):
    """Attempt to restore against a non-pristine system."""


class InvalidBackup(BackupError):
    """Backup corrupt or not valid."""


class disable_foreign_key_checks(object):
    def __init__(self, connection):
        self.connection = connection

    def __enter__(self):
        if self.connection.vendor == 'mysql':
            cursor = self.connection.cursor()
            cursor.execute('SET foreign_key_checks = 0')

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection.vendor == 'mysql':
            cursor = self.connection.cursor()
            cursor.execute('SET foreign_key_checks = 1')
        return False


def read_metadata(zipfile):
    for info in zipfile.infolist():
        basename = os.path.basename(info.filename)
        if basename == METADATA_FILENAME:
            meta_file = zipfile.read(info.filename)
            return kbjson.loads(meta_file)
    return {}


def tbl(model):
    return str(model._meta.db_table)


def get_models_to_backup():
    """Returns models that should be saved during backup."""
    return [m for m in get_models() if tbl(m) not in BACKUP_SKIPPED_TABLE_NAMES]


def get_models_to_erase():
    """Returns models that should be erased [prior to restore]."""
    return [m for m in get_models_to_backup() if tbl(m) not in ERASE_SKIPPED_TABLE_NAMES]

get_models_to_restore = get_models_to_erase


def erase_model_table(model, must_truncate=False):
    table = tbl(model)
    cursor = connection.cursor()
    if connection.vendor == 'mysql':
        with disable_foreign_key_checks(connection):
            cursor.execute('TRUNCATE TABLE `{}`'.format(table))
            cursor.execute('ALTER TABLE `{}` AUTO_INCREMENT = 1'.format(table))
    elif connection.vendor == 'sqlite':
        cursor.execute('DELETE FROM {}'.format(table))
    else:
        if must_truncate:
            raise ValueError('Truncate on vendor "{}" unsupported'.format(connection.vendor))
        else:
            model.objects.all().delete()


@transaction.atomic
def create_backup_tree(date, storage, include_media=True):
    """Creates filesystem tree of backup data."""
    backup_dir = tempfile.mkdtemp()
    metadata = {}

    # Save databases.
    tables_dir = os.path.join(backup_dir, TABLES_DIRNAME)
    os.makedirs(tables_dir)

    all_models = get_models_to_backup()
    metadata[META_NUM_TABLES] = len(all_models)

    for model in all_models:
        table_name = model._meta.db_table
        output_filename = os.path.join(tables_dir, table_name + '.json')
        logger.debug('+++ Creating {}'.format(output_filename))
        with open(output_filename, 'w') as out:
            serializers.serialize('json', model.objects.all(), indent=2, stream=out)

    # Save stored media.
    metadata[META_NUM_MEDIA_FILES] = 0

    def add_files(storage, dirname, destdir):
        """Recursively copies all files in `dirname` to `destdir`."""
        subdirs, files = storage.listdir(dirname)
        for filename in files:
            full_filename = os.path.join(dirname, filename)
            output_filename = os.path.join(destdir, full_filename)
            output_dirname = os.path.dirname(output_filename)
            if not os.path.exists(output_dirname):
                os.makedirs(output_dirname)
            with storage.open(full_filename, 'r') as srcfile:
                with open(output_filename, 'w') as dstfile:
                    logger.debug('+++ Creating {}'.format(output_filename))
                    shutil.copyfileobj(srcfile, dstfile)
                    metadata[META_NUM_MEDIA_FILES] += 1
        for subdir in subdirs:
            add_files(storage, os.path.join((dirname, subdir)), destdir)

    if include_media:
        destdir = os.path.join(backup_dir, 'media')
        for media_dir in MEDIA_WHITELIST:
            if storage.exists(media_dir):
                add_files(storage, media_dir, destdir)
    else:
        logger.warning('Not including media.')

    # Store metadata file.
    metadata[META_SERVER_NAME] = models.KegbotSite.get().title
    metadata[META_SERVER_VERSION] = get_version()
    metadata[META_CREATED_TIME] = isodate.datetime_isoformat(date)
    metadata[META_BACKUP_FORMAT] = BACKUP_FORMAT
    metadata_filename = os.path.join(backup_dir, METADATA_FILENAME)
    with open(metadata_filename, 'w') as outfile:
        json.dump(metadata, outfile, sort_keys=True, indent=2)

    valid = False
    try:
        verify_backup_directory(backup_dir)
        valid = True
        return backup_dir
    finally:
        if not valid:
            shutil.rmtree(backup_dir)


def create_backup_zip(backup_dir, backup_name):
    """Creates a zipfile based on a tree created with `create_backup_tree()`."""
    zipfile_fileno, zipfile_path = tempfile.mkstemp()
    zipfile_fd = os.fdopen(zipfile_fileno, 'w')
    zf = zipfile.ZipFile(zipfile_fd, 'w')

    for dirname, subdirs, files in os.walk(backup_dir):
        for filename in files:
            full_path = os.path.join(dirname, filename)
            rel_path = os.path.relpath(full_path, backup_dir)
            archive_path = os.path.join(backup_name, rel_path)
            zf.write(full_path, archive_path)
            logger.debug('Added to zip: {}'.format(archive_path))

    zf.close()
    return zipfile_path


def backup(storage=default_storage, include_media=True):
    """Creates a new backup archive.

    Returns:
        A path to the stored zip file, in terms of the current storage class.
    """
    date = timezone.now()
    site_slug = slugify(models.KegbotSite.get().title)
    date_str = date.strftime('%Y%m%d-%H%M%S')
    backup_name = '{slug}-{date}'.format(slug=site_slug, date=date_str)

    backup_dir = create_backup_tree(date=date, storage=storage, include_media=include_media)
    try:
        temp_zip = create_backup_zip(backup_dir, backup_name)
        try:
            # Append sha1sum.
            sha1 = hashlib.sha1()
            with open(temp_zip, 'rb') as f:
                for chunk in iter(lambda: f.read(2 ** 20), b''):
                    sha1.update(chunk)
            digest = sha1.hexdigest()
            saved_zip_name = os.path.join(BACKUPS_DIRNAME,
                '{}-{}.zip'.format(backup_name, digest))
            with open(temp_zip, 'r') as temp_zip_file:
                ret = storage.save(saved_zip_name, temp_zip_file)
                return ret
        finally:
            os.unlink(temp_zip)
    finally:
        shutil.rmtree(backup_dir)


def extract_backup(backup_file):
    assert sys.version_info[:3] >= (2, 7, 4), "Unsafe to extract ZIPs in this Python version"
    backup_dir = tempfile.mkdtemp()
    logger.debug('Extracting backup to {}'.format(backup_dir))
    zf = zipfile.ZipFile(backup_file, mode='r')
    zf.extractall(path=backup_dir)
    return backup_dir


def verify_backup_directory(backup_dir):
    metadata_file = os.path.join(backup_dir, METADATA_FILENAME)
    if not os.path.exists(metadata_file):
        raise InvalidBackup('Metadata file does not exist')

    metadata = kbjson.loads(open(metadata_file, 'r').read())
    format = metadata.get(META_BACKUP_FORMAT)
    if format != BACKUP_FORMAT:
        raise InvalidBackup('Unsupported backup format: {}'.format(format))

    for model in get_models_to_restore():
        table_json = os.path.join(backup_dir, TABLES_DIRNAME, tbl(model) + '.json')
        if not os.path.exists(table_json):
            raise InvalidBackup('Backup missing file {}'.format(table_json))


def restore_tables(backup_dir):
    """Loads database tables from `backup_dir`."""
    for model in get_models_to_restore():
        if model.objects.all().count() > 0:
            raise AlreadyInstalledError('Table "{}" is not empty, cannot restore. '
                'Run "kegbot erase" first.'.format(model._meta.db_table))
    tables_dir = os.path.join(backup_dir, TABLES_DIRNAME)

    with disable_foreign_key_checks(connection):
        for model in get_models_to_restore():
            table = tbl(model)
            table_file = os.path.join(tables_dir, table + '.json')
            logger.debug('Restoring table {}'.format(table))
            with open(table_file, 'r') as table_fp:
                data = table_fp.read()
                objects = serializers.deserialize('json', data)
                for obj in objects:
                    obj.save()


def restore_media(backup_dir, storage):
    media_dir = os.path.join(backup_dir, 'media')

    for dirname, subdirs, files in os.walk(media_dir):
        for filename in files:
            full_path = os.path.join(dirname, filename)
            rel_path = os.path.relpath(full_path, media_dir)
            with open(full_path, 'r') as data:
                logger.debug('+++ Restoring file {}'.format(rel_path))
                storage.save(rel_path, data)


def check_app_migrations(app_name, backup_migrations):
    """Asserts that latest migration for `app_name` match those saved in
       `backup_migrations`.
    """
    latest_backup = latest_db = None
    for m in backup_migrations:
        if m.object.app_name == app_name:
            if not latest_backup or latest_backup.migration < m.object.migration:
                latest_backup = m.object

    qs = south_models.MigrationHistory.objects.filter(app_name=app_name)
    qs = qs.order_by('-migration')
    if qs:
        latest_db = qs[0]

    if latest_backup is None:
        raise InvalidBackup('No migrations in backup for app "{}"'.format(app_name))
    if latest_db is None:
        raise InvalidBackup('No migrations in database for app "{}"'.format(app_name))

    logger.debug('App "{}" migrations: backup={} db={}'.format(
        app_name, latest_backup.migration, latest_db.migration))

    if latest_backup.migration != latest_db.migration:
        raise InvalidBackup('Backup migration mismatch (db={}).  Try "kegbot migrate {} {}" first.'.format(
            latest_db.migration, app_name, latest_backup.migration))


def check_migrations(backup_dir):
    tables_dir = os.path.join(backup_dir, TABLES_DIRNAME)
    migration_filename = os.path.join(tables_dir, 'south_migrationhistory.json')
    with open(migration_filename, 'r') as migration_fp:
        backup_migrations = list(serializers.deserialize('json', migration_fp.read()))

    for app_name in APP_NAMES:
        logger.debug('Checking migrations for app {}'.format(app_name))
        check_app_migrations(app_name, backup_migrations)


def restore_from_directory(backup_dir, storage=default_storage):
    logger.info('Restoring from {} ...'.format(backup_dir))
    verify_backup_directory(backup_dir)
    with transaction.atomic():
        check_migrations(backup_dir)
        restore_tables(backup_dir)
        restore_media(backup_dir, storage)
    logger.info('Restore completed successfully.')


def restore(backup_file):
    """Restores from a backup zipfile.

    The site must be erased prior to running restore.
    """
    logger.info('Restoring from {} ...'.format(backup_file))
    unzipped_dir = extract_backup(backup_file)
    try:
        dirs = os.listdir(unzipped_dir)
        if len(dirs) != 1:
            raise InvalidBackup('Expected exactly one directory in archive.')
        backup_dir = os.path.join(unzipped_dir, dirs[0])
        restore_from_directory(backup_dir)
    finally:
        shutil.rmtree(unzipped_dir)


def erase(storage=default_storage):
    """Erases ALL site data (database tables, media files)."""
    logger.info('Erasing tables ...')
    with transaction.atomic():
        with disable_foreign_key_checks(connection):
            for model in get_models_to_erase():
                logger.debug('--- Erasing {}'.format(tbl(model)))
                erase_model_table(model, must_truncate=True)

    def delete_files(dirname):
        subdirs, files = storage.listdir(dirname)
        for filename in files:
            full_name = os.path.join(dirname, filename)
            logger.debug('Deleting file: {}'.format(full_name))
            storage.delete(full_name)
        for subdir in subdirs:
            delete_files(dirname)

    logger.info('Erasing media ...')
    for media_dir in MEDIA_WHITELIST:
        if storage.exists(media_dir):
            delete_files(media_dir)

    logger.info('Done.')
