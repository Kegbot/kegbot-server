#!/bin/sh
# Builds a "v1.3 site" backup zip for upgrade-path testing.
#
# Usage: build-legacy-backup.sh <output.zip>
#
# Requires a fresh, empty database at DATABASE_URL (mysql or postgres),
# redis at REDIS_URL, and a writable KEGBOT_DATA_DIR. The database is
# populated from testdata/demo-site.json, which records a site at
# server_version 1.3.0, then dumped with `kegbot backup` (format 2).
#
# Normally run inside docker compose via bin/generate-legacy-backups.sh,
# which builds the frozen zips checked in under testdata/legacy-backups/.

set -eu

OUT="${1:?usage: $0 <output.zip>}"

bin/kegbot migrate --noinput -v 0
bin/kegbot loaddata testdata/demo-site.json

ZIP_PATH=$(bin/kegbot backup | sed -n 's/^Path: //p')
if [ -z "$ZIP_PATH" ] || [ ! -f "$ZIP_PATH" ]; then
    echo "error: backup zip not found (got: '$ZIP_PATH')" >&2
    exit 1
fi

cp "$ZIP_PATH" "$OUT"
echo "Wrote $OUT"
