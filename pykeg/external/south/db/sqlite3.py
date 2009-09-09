import inspect
from django.db import connection
from south.db import generic

class DatabaseOperations(generic.DatabaseOperations):

    """
    SQLite3 implementation of database operations.
    """
    
    backend_name = "sqlite3"

    # SQLite ignores foreign key constraints. I wish I could.
    supports_foreign_keys = False
    defered_alters = {}
    def _defer_alter_sqlite_table(self, table_name, field_renames={}):
        table_renames = self.defered_alters.get(table_name, {})
        table_renames.update(field_renames)
        self.defered_alters[table_name] = table_renames

    # You can't add UNIQUE columns with an ALTER TABLE.
    def add_column(self, table_name, name, field, *args, **kwds):
        # Run ALTER TABLE with no unique column
        unique, field._unique, field.db_index = field.unique, False, False
        # If it's not nullable, and has no default, raise an error (SQLite is picky)
        if not field.null and (not field.has_default() or field.get_default() is None):
            raise ValueError("You cannot add a null=False column without a default value.")
        generic.DatabaseOperations.add_column(self, table_name, name, field, *args, **kwds)
        # If it _was_ unique, make an index on it.
        if unique:
            self.create_index(table_name, [field.column], unique=True)
    
    def _alter_sqlite_table(self, table_name, field_renames={}):
        
        # Detect the model for the given table name
        model = None
        for omodel in self.current_orm:
            if omodel._meta.db_table == table_name:
                model = omodel
        if model is None:
            raise ValueError("Cannot find ORM model for '%s'." % table_name)

        temp_name = table_name + "_temporary_for_schema_change"
        self.rename_table(table_name, temp_name)
        fields = [(fld.name, fld) for fld in model._meta.fields]
        self.create_table(table_name, fields)

        columns = [fld.column for name, fld in fields]
        self.copy_data(temp_name, table_name, columns, field_renames)
        self.delete_table(temp_name, cascade=False)
    
    def alter_column(self, table_name, name, field, explicit_name=True):
        
        raise NotImplementedError("The SQLite backend does not yet support alter_column.")
        # Do initial setup
        if hasattr(field, 'south_init'):
            field.south_init()
        field.set_attributes_from_name(name)
        
        self._defer_alter_sqlite_table(table_name, {name: field.column})

    def delete_column(self, table_name, column_name):
        
        raise NotImplementedError("The SQLite backend does not yet support delete_column.")
        self._defer_alter_sqlite_table(table_name)
    
    def rename_column(self, table_name, old, new):
        self._defer_alter_sqlite_table(table_name, {old: new})
    
    # Nor unique creation
    def create_unique(self, table_name, columns):
        """
        Not supported under SQLite.
        """
        print "   ! WARNING: SQLite does not support adding unique constraints. Ignored."
    
    # Nor unique deletion
    def delete_unique(self, table_name, columns):
        """
        Not supported under SQLite.
        """
        print "   ! WARNING: SQLite does not support removing unique constraints. Ignored."
    
    # No cascades on deletes
    def delete_table(self, table_name, cascade=True):
        generic.DatabaseOperations.delete_table(self, table_name, False)

    def copy_data(self, src, dst, fields, field_renames={}):
        qn = connection.ops.quote_name
        q_fields = [field for field in fields]
        for old, new in field_renames.items():
            q_fields[q_fields.index(new)] = "%s AS %s" % (old, qn(new))
        sql = "INSERT INTO %s SELECT %s FROM %s;" % (qn(dst), ', '.join(q_fields), qn(src))
        self.execute(sql)

    def execute_deferred_sql(self):
        """
        Executes all deferred SQL, resetting the deferred_sql list
        """
        for table_name, params in self.defered_alters.items():
            self._alter_sqlite_table(table_name, params)
        self.defered_alters = {}

        generic.DatabaseOperations.execute_deferred_sql(self)
