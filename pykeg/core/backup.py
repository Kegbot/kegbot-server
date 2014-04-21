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
import datetime
import isodate
import tempfile
import shutil
import json
import zipfile

from pykeg.core import models
from pykeg.core.util import get_version
from kegbot.util import kbjson

from django.core.files.storage import get_storage_class
from django.core import serializers
from django.db import transaction
from django.db.models import Q, get_app, get_models
from django.utils import timezone
from django.utils.text import slugify

logger = logging.getLogger(__name__)

# Tables to ignore when creating/loading backups.
SKIPPED_TABLE_NAMES = [
    'django_admin_log',
    'django_session',
    'django_content_type',
    'auth_group',
    'auth_permission'
]

# Whitelist of directories to include from storage backend.
MEDIA_WHITELIST = [
    'pics'
]

# Metadata key names.
METADATA_FILENAME = 'metadata.json'
META_CREATED_TIME = 'created_time'
META_NUM_MEDIA_FILES = 'num_media_files'
META_NUM_TABLES = 'num_tables'
META_SERVER_VERSION = 'server_version'
META_SERVER_NAME = 'server_name'

BACKUPS_DIRNAME = 'backups'
TABLES_DIRNAME = 'tables'

def read_metadata(zipfile):
    for info in zipfile.infolist():
        basename = os.path.basename(info.filename)
        if basename == METADATA_FILENAME:
            meta_file = zipfile.read(info.filename)
            return kbjson.loads(meta_file)
    return {}

@transaction.atomic
def create_backup_tree(date):
    """Creates filesystem tree of backup data."""
    backup_dir = tempfile.mkdtemp()
    metadata = {}

    # Save databases.
    tables_dir = os.path.join(backup_dir, TABLES_DIRNAME)
    os.makedirs(tables_dir)

    all_models = [m for m in get_models() if m._meta.db_table not in SKIPPED_TABLE_NAMES]
    metadata[META_NUM_TABLES] = len(all_models)

    for model in all_models:
        table_name = model._meta.db_table
        output_filename = os.path.join(tables_dir, table_name + '.json')
        logger.info('+++ Creating {}'.format(output_filename))
        with open(output_filename, 'w') as out:
            serializers.serialize('json', model.objects.all(), indent=2, stream=out)

    # Save stored media.
    storage = get_storage_class()()
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
                    logger.info('+++ Creating {}'.format(output_filename))
                    shutil.copyfileobj(srcfile, dstfile)
                    metadata[META_NUM_MEDIA_FILES] += 1
        for subdir in subdirs:
            add_files(storage, os.path.join((dirname, subdir)), destdir)

    destdir = os.path.join(backup_dir, 'media')
    for media_dir in MEDIA_WHITELIST:
        add_files(storage, media_dir, destdir)

    # Store metadata file.
    metadata[META_SERVER_NAME] = models.KegbotSite.get().title
    metadata[META_SERVER_VERSION] = get_version()
    metadata[META_CREATED_TIME] = isodate.datetime_isoformat(date)
    metadata_filename = os.path.join(backup_dir, METADATA_FILENAME)
    with open(metadata_filename, 'w') as outfile:
        json.dump(metadata, outfile, sort_keys=True, indent=2)

    return backup_dir

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
            logger.info('Added to zip: {}'.format(archive_path))

    zf.close()
    return zipfile_path

def backup():
    """Creates a new backup archive.

    Returns:
        A path to the stored zip file, in terms of the current storage class.
    """
    date = timezone.now()
    site_slug = slugify(models.KegbotSite.get().title)
    date_str = date.strftime('%Y%m%d-%H%M%S')
    backup_name = '{site_slug}-{date_str}'.format(**vars())

    backup_dir = create_backup_tree(date=date)
    try:
        temp_zip = create_backup_zip(backup_dir, backup_name)
        try:
            # Append sha1sum.
            sha1 = hashlib.sha1()
            with open(temp_zip, 'rb') as f:
                for chunk in iter(lambda: f.read(2**20), b''):
                    sha1.update(chunk)
            digest = sha1.hexdigest()
            saved_zip_name = os.path.join(BACKUPS_DIRNAME,
                '{}-{}.zip'.format(backup_name, digest))
            with open(temp_zip, 'r') as temp_zip_file:
                storage = get_storage_class()()
                ret = storage.save(saved_zip_name, temp_zip_file)
                return ret
        finally:
            # Remove temp_zip.
            pass
    finally:
        shutil.rmtree(backup_dir)
