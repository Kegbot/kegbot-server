"""Wraps some common database problems in usable errors."""

from django.db import connection
from django.db.migrations.executor import MigrationExecutor


class DatabaseStatusError(Exception):
    """General error thrown when the database is... Not Good."""


class DatabaseNotInitialized(DatabaseStatusError):
    """Thrown when the db doesn't appear to be initialized."""


class NeedMigration(DatabaseStatusError):
    """Thrown when a migration is needed."""
    def __init__(self, migration_name):
        super(NeedMigration, self).__init__('Migration "{}" not applied'.format(migration_name))
        self.migration_name = migration_name


def check_db_status():
    tables = connection.introspection.table_names()
    if 'django_migrations' not in tables:
        raise DatabaseNotInitialized()

    executor = MigrationExecutor(connection)
    targets = executor.loader.graph.leaf_nodes()
    plan = executor.migration_plan(targets)
    if plan:
        migration = plan[0][0]
        raise NeedMigration(migration.name)
