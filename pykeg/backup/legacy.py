"""Restore support for legacy format-1 backups (Kegbot v1.1.x).

Format-1 backups store per-table Django fixture JSON under `tables/`
rather than a SQL dump. The v1.1 restore procedure loaded those fixtures
through the ORM into a freshly-migrated database, so the modern
equivalent does the same: migrate to the current schema, transform the
fixtures across the (small) v1.1 -> v1.2/1.3 model changes, and load
them with `loaddata`.

Because data lands directly in the current schema, a completed legacy
restore needs no separate `kegbot upgrade`: the stored server version is
set to the current version and stats are regenerated as a final step.
"""

import glob
import json
import logging
import os
import tempfile

from django.apps import apps
from django.core.management import call_command
from django.core.management.color import no_style
from django.db import connection

from .exceptions import InvalidBackup

logger = logging.getLogger(__name__)

LEGACY_BACKUP_FORMAT = 1
TABLES_DIRNAME = "tables"

# Tables that existed in v1.1 but have no modern equivalent.
IGNORED_TABLES = {"south_migrationhistory"}


def load_table_dumps(backup_dir):
    """Reads all fixture files from a format-1 backup's `tables/` dir."""
    tables_dir = os.path.join(backup_dir, TABLES_DIRNAME)
    if not os.path.isdir(tables_dir):
        raise InvalidBackup("Backup does not contain a tables/ directory")

    tables = {}
    for path in sorted(glob.glob(os.path.join(tables_dir, "*.json"))):
        name = os.path.basename(path)[: -len(".json")]
        with open(path) as f:
            tables[name] = json.load(f)
    return tables


def transform_tables(tables):
    """Transforms v1.1-era fixtures for the current models.

    Applies the same changes the core 0002-0004 migrations performed on
    live data:

      - keg: finished/online -> status ("on_tap" when a tap's current_keg
        points at the keg, else "finished" or "available")
      - kegtap: description -> notes
      - kegbotsite: drop check_for_updates
      - drinkingsession: timezone <- site timezone

    Returns a flat list of serialized objects, ready for `loaddata`.
    """
    tables = {k: v for k, v in tables.items() if k not in IGNORED_TABLES}

    site_tz = "UTC"
    for row in tables.get("core_kegbotsite", []):
        fields = row["fields"]
        site_tz = fields.get("timezone", site_tz)
        fields.pop("check_for_updates", None)

    on_tap_kegs = {
        row["fields"]["current_keg"]
        for row in tables.get("core_kegtap", [])
        if row["fields"].get("current_keg")
    }
    for row in tables.get("core_keg", []):
        fields = row["fields"]
        finished = fields.pop("finished", False)
        fields.pop("online", None)
        if row["pk"] in on_tap_kegs:
            fields["status"] = "on_tap"
        elif finished:
            fields["status"] = "finished"
        else:
            fields["status"] = "available"

    for row in tables.get("core_kegtap", []):
        fields = row["fields"]
        if "description" in fields:
            fields["notes"] = fields.pop("description")

    for row in tables.get("core_drinkingsession", []):
        row["fields"].setdefault("timezone", site_tz)

    objects = []
    for rows in tables.values():
        objects.extend(rows)
    return objects


def load_data(objects):
    """Loads transformed fixture objects into the current database."""
    # loaddata (rather than direct deserialization) so foreign key checks
    # are deferred for the duration of the load.
    with tempfile.TemporaryDirectory() as tmpdir:
        fixture_path = os.path.join(tmpdir, "legacy_backup.json")
        with open(fixture_path, "w") as f:
            json.dump(objects, f)
        call_command("loaddata", fixture_path, verbosity=0)

    # Rows were inserted with explicit pks; realign auto-increment
    # sequences (needed on postgres; a no-op elsewhere). Only the loaded
    # models: other apps may have models without tables.
    loaded_models = {apps.get_model(o["model"]) for o in objects}
    sequence_sql = connection.ops.sequence_reset_sql(no_style(), sorted(loaded_models, key=str))
    if sequence_sql:
        with connection.cursor() as cursor:
            for statement in sequence_sql:
                cursor.execute(statement)


def restore_data(backup_dir):
    """Restores a format-1 backup's data into a migrated, empty database.

    The caller is responsible for schema (migrations) and media.
    """
    from pykeg.core import models, stats
    from pykeg.core.util import get_version

    from .exceptions import AlreadyInstalledError

    if models.KegbotSite.objects.exists():
        raise AlreadyInstalledError("You must erase this system before restoring.")

    tables = load_table_dumps(backup_dir)
    objects = transform_tables(tables)
    logger.info(f"Loading {len(objects)} records from legacy backup ...")
    load_data(objects)

    # Data now lives in the current schema; no separate upgrade step remains.
    site = models.KegbotSite.get()
    site.server_version = get_version()
    site.save(update_fields=["server_version"])

    logger.info("Regenerating stats ...")
    stats.invalidate_all()
    stats.rebuild_from_id(0)
