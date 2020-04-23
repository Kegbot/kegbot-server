# Copyright 2014 Kegbot Project contributors
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
       backup.sql        - backup sql data

The zipfile name takes the form <backup-name>-<sha1sum>.zip.

`backup-name` takes the form <site-title>-<YYMMDD-HHMMSS>, where
`site-title` is the slugified version of the current Kegbot site's
title.

Note that both the zipfile name and the backup file dirname are
informational and may change in a future version.

metadata.json consists of backup-related metadata:
  'created_time': ISO8601 timestamp at backup create
  'num_media_files': number of files in the 'media/' folder
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

from pykeg.core.util import get_version
from pykeg.util import kbjson

from .exceptions import BackupError, InvalidBackup, AlreadyInstalledError

from django.conf import settings
from django.core.files.storage import default_storage
from django.db import connection
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

logger = logging.getLogger(__name__)


# Whitelist of directories to include from storage backend.
MEDIA_WHITELIST = ["pics"]

# Metadata key names.
METADATA_FILENAME = "metadata.json"
SQL_FILENAME = "kegbot.sql"
META_CREATED_TIME = "created_time"
META_NUM_MEDIA_FILES = "num_media_files"
META_SERVER_VERSION = "server_version"
META_SERVER_NAME = "server_name"
META_BACKUP_FORMAT = "backup_format"
META_DB_ENGINE = "db_engine"

DEFAULT_DB = "default"
BACKUPS_DIRNAME = "backups"

# Current protocol.
BACKUP_FORMAT = 2


ENGINE_MYSQL = "mysql"
ENGINE_POSTGRES = "postgres"
ENGINE_UNKNOWN = "unknown"


# TODO(mikey): Lazy init.
engine = settings.DATABASES.get(DEFAULT_DB, {}).get("ENGINE", "unknown")
if "mysql" in engine:
    from . import mysql as db_impl
elif "postgres" in engine:
    from . import postgres as db_impl
else:
    from . import unknown_engine as db_impl


def get_title():
    with connection.cursor() as c:
        c.execute("SELECT title FROM core_kegbotsite WHERE name = 'default'")
        row = c.fetchone()
    if row:
        return row[0]
    return "kegbot"


def read_metadata(zipfile):
    """Reads and returns metadata from a backup zipfile."""
    for info in zipfile.infolist():
        basename = os.path.basename(info.filename)
        if basename == METADATA_FILENAME:
            meta_file = zipfile.read(info.filename)
            return kbjson.loads(meta_file)
    return {}


@transaction.atomic
def create_backup_tree(date, storage, include_media=True):
    """Builds a complete backup in a temporary directory, return the path."""
    backup_dir = tempfile.mkdtemp()
    metadata = {}

    # Save databases.
    output_filename = os.path.join(backup_dir, SQL_FILENAME)
    with open(output_filename, "w") as out_fd:
        db_impl.dump(out_fd)

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
            with storage.open(full_filename, "r") as srcfile:
                with open(output_filename, "w") as dstfile:
                    logger.debug("+++ Creating {}".format(output_filename))
                    shutil.copyfileobj(srcfile, dstfile)
                    metadata[META_NUM_MEDIA_FILES] += 1
        for subdir in subdirs:
            add_files(storage, os.path.join((dirname, subdir)), destdir)

    if include_media:
        destdir = os.path.join(backup_dir, "media")
        for media_dir in MEDIA_WHITELIST:
            if storage.exists(media_dir):
                add_files(storage, media_dir, destdir)
    else:
        logger.warning("Not including media.")

    # Store metadata file.
    metadata[META_SERVER_NAME] = get_title()
    metadata[META_SERVER_VERSION] = get_version()
    metadata[META_CREATED_TIME] = isodate.datetime_isoformat(date)
    metadata[META_DB_ENGINE] = db_impl.engine_name()
    metadata[META_BACKUP_FORMAT] = BACKUP_FORMAT
    metadata_filename = os.path.join(backup_dir, METADATA_FILENAME)
    with open(metadata_filename, "w") as outfile:
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
    zipfile_fd = os.fdopen(zipfile_fileno, "w")
    zf = zipfile.ZipFile(zipfile_fd, "w")

    for dirname, subdirs, files in os.walk(backup_dir):
        for filename in files:
            full_path = os.path.join(dirname, filename)
            rel_path = os.path.relpath(full_path, backup_dir)
            archive_path = os.path.join(backup_name, rel_path)
            zf.write(full_path, archive_path)
            logger.debug("Added to zip: {}".format(archive_path))

    zf.close()
    return zipfile_path


def backup(storage=default_storage, include_media=True):
    """Creates a new backup archive.

    Returns:
        A path to the stored zip file, in terms of the current storage class.
    """
    date = timezone.now()
    site_slug = slugify(get_title())
    date_str = date.strftime("%Y%m%d-%H%M%S")
    backup_name = "{slug}-{date}".format(slug=site_slug, date=date_str)

    backup_dir = create_backup_tree(date=date, storage=storage, include_media=include_media)
    try:
        temp_zip = create_backup_zip(backup_dir, backup_name)
        try:
            # Append sha1sum.
            sha1 = hashlib.sha1()
            with open(temp_zip, "rb") as f:
                for chunk in iter(lambda: f.read(2 ** 20), b""):
                    sha1.update(chunk)
            digest = sha1.hexdigest()
            saved_zip_name = os.path.join(BACKUPS_DIRNAME, "{}-{}.zip".format(backup_name, digest))
            with open(temp_zip, "r") as temp_zip_file:
                ret = storage.save(saved_zip_name, temp_zip_file)
                return ret
        finally:
            os.unlink(temp_zip)
    finally:
        shutil.rmtree(backup_dir)


def extract_backup(backup_file):
    assert sys.version_info[:3] >= (2, 7, 4), "Unsafe to extract ZIPs in this Python version"
    backup_dir = tempfile.mkdtemp()
    logger.debug("Extracting backup to {}".format(backup_dir))
    zf = zipfile.ZipFile(backup_file, mode="r")
    zf.extractall(path=backup_dir)
    return backup_dir


def verify_backup_directory(backup_dir):
    metadata_file = os.path.join(backup_dir, METADATA_FILENAME)
    if not os.path.exists(metadata_file):
        raise InvalidBackup("Metadata file does not exist")

    if not os.path.exists(metadata_file):
        raise InvalidBackup("SQL dumpfile does not exist")

    metadata = kbjson.loads(open(metadata_file, "r").read())
    format = metadata.get(META_BACKUP_FORMAT)
    if format != BACKUP_FORMAT:
        raise InvalidBackup("Unsupported backup format: {}".format(format))

    return metadata


def restore_media(backup_dir, storage):
    media_dir = os.path.join(backup_dir, "media")

    for dirname, subdirs, files in os.walk(media_dir):
        for filename in files:
            full_path = os.path.join(dirname, filename)
            rel_path = os.path.relpath(full_path, media_dir)
            with open(full_path, "r") as data:
                logger.debug("+++ Restoring file {}".format(rel_path))
                storage.save(rel_path, data)


def restore_from_directory(backup_dir, storage=default_storage):
    logger.info("Restoring from {} ...".format(backup_dir))

    if db_impl.is_installed():
        raise AlreadyInstalledError("You must erase this system before restoring.")

    metadata = verify_backup_directory(backup_dir)
    current_engine = db_impl.engine_name()
    saved_engine = metadata[META_DB_ENGINE]
    if current_engine != saved_engine:
        raise BackupError(
            "Current DB is {}; cannot restore from {}".format(current_engine, db_impl)
        )

    input_filename = os.path.join(backup_dir, SQL_FILENAME)
    with open(input_filename, "r") as in_fd:
        db_impl.restore(in_fd)

    restore_media(backup_dir, storage)

    logger.info("Restore completed successfully.")


def restore(backup_file):
    """Restores from a backup zipfile or directory.

    The site must be erased prior to running restore.
    """
    if os.path.isdir(backup_file):
        restore_from_directory(backup_file)
        return

    logger.info("Restoring from {} ...".format(backup_file))
    unzipped_dir = extract_backup(backup_file)
    try:
        dirs = os.listdir(unzipped_dir)
        if len(dirs) != 1:
            raise InvalidBackup("Expected exactly one directory in archive.")
        backup_dir = os.path.join(unzipped_dir, dirs[0])
        restore_from_directory(backup_dir)
    finally:
        shutil.rmtree(unzipped_dir)


def erase(storage=default_storage):
    """Erases ALL site data (database tables, media files)."""
    logger.info("Erasing tables ...")
    db_impl.erase()

    def delete_files(dirname):
        subdirs, files = storage.listdir(dirname)
        for filename in files:
            full_name = os.path.join(dirname, filename)
            logger.debug("Deleting file: {}".format(full_name))
            storage.delete(full_name)
        for subdir in subdirs:
            delete_files(dirname)

    logger.info("Erasing media ...")
    for media_dir in MEDIA_WHITELIST:
        if storage.exists(media_dir):
            delete_files(media_dir)

    logger.info("Done.")
