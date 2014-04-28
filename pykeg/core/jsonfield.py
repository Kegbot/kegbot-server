from __future__ import absolute_import

from jsonfield import JSONField as BaseJSONField


class JSONField(BaseJSONField):
    pass

try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^pykeg.core.jsonfield\.JSONField"])
except ImportError:
    pass
