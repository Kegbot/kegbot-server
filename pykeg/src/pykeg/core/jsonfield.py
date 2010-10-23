# Cloned from django-extensions project: django_extensions.db.fields.json
# django_extensions has the following license:
#
#   Copyright (c) 2007 Michael Trier
#
#   Permission is hereby granted, free of charge, to any person obtaining a copy
#   of this software and associated documentation files (the "Software"), to
#   deal in the Software without restriction, including without limitation the
#   rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#   sell copies of the Software, and to permit persons to whom the Software is
#   furnished to do so, subject to the following conditions:
#
#   The above copyright notice and this permission notice shall be included in
#   all copies or substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#   FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
#   IN THE SOFTWARE.
#
# Local differences from upstream version:
#   - disabled assert in JSONEncoder
#   - added south introspection rules
#   - use kbjson common json encode/decode methods

"""
JSONField automatically serializes most Python terms to JSON data.
Creates a TEXT field with a default value of "{}".  See test_json.py for
more information.

 from django.db import models
 from django_extensions.db.fields import json

 class LOL(models.Model):
     extra = json.JSONField()
"""

from django.db import models
from pykeg.core import kbjson

class JSONDict(dict):
  """
  Hack so repr() called by dumpdata will output JSON instead of
  Python formatted data.  This way fixtures will work!
  """
  def __repr__(self):
    return kbjson.dumps(self)

class JSONField(models.TextField):
  """JSONField is a generic textfield that neatly serializes/unserializes
  JSON objects seamlessly.  Main thingy must be a dict object."""

  # Used so to_python() is called
  __metaclass__ = models.SubfieldBase

  def __init__(self, *args, **kwargs):
    if 'default' not in kwargs:
      kwargs['default'] = '{}'
    models.TextField.__init__(self, *args, **kwargs)

  def to_python(self, value):
    """Convert our string value to JSON after we load it from the DB"""
    if not value:
      return {}
    elif isinstance(value, basestring):
      res = kbjson.loads(value)
      assert isinstance(res, dict)
      return JSONDict(**res)
    else:
      return value

  def get_db_prep_save(self, value):
    """Convert our JSON object to a string before we save"""
    if not value:
      return super(JSONField, self).get_db_prep_save("")
    else:
      return super(JSONField, self).get_db_prep_save(kbjson.dumps(value))

try:
  from south.modelsinspector import add_introspection_rules
except ImportError:
  pass
else:
  add_introspection_rules([
    ([JSONField], [], {}),
    ], ["^pykeg\.core\.jsonfield\.JSONField"])
