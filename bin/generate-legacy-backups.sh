#!/bin/sh
# Generates the frozen v1.3 backup fixtures with docker compose.
#
# Usage: bin/generate-legacy-backups.sh
#
# Writes testdata/legacy-backups/kegbot-v1.3-{mysql,postgres}.zip, built
# from testdata/demo-site.json against pinned mysql/postgres images.
# Commit the zips to update the fixtures used by the Legacy Upgrade Test
# workflow.
#
# Regenerate deliberately, not routinely: the fixtures are frozen so that
# future migrations are tested against a database as it existed at v1.3.

set -eu

cd "$(dirname "$0")/.."
mkdir -p testdata/legacy-backups

COMPOSE="docker compose -f testdata/legacy-backup-compose.yml"
trap '$COMPOSE down -v --remove-orphans' EXIT

$COMPOSE build generate-mysql
$COMPOSE run --rm generate-mysql
$COMPOSE run --rm generate-postgres

echo ""
echo "Fixtures written:"
ls -l testdata/legacy-backups/*.zip
