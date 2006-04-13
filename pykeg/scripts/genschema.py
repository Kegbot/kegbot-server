#!/usr/bin/python

# hacks -- remove me when properly packaged
import sys
sys.path.append('.')
sys.path.append('..')
import sqlobject
import Backend
import inspect

Backend.setup('mysql://')
classes = inspect.getmembers(Backend, inspect.isclass)

print '-- kegbot sql schema'
print '-- schema version: %i' % Backend.SCHEMA_VERSION

for clsname, cls in classes:
   if not issubclass(cls, sqlobject.SQLObject):
      continue
   if cls == sqlobject.SQLObject:
      continue
   print '-- table: %s' % (clsname,)
   print cls.createTableSQL().strip() + ';\n\n'


