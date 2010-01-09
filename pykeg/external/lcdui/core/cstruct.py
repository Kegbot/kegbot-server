"""
cstruct.py
by mike wakerly - http://hoho.com/mike/
"""

import crc16
import struct

class cStruct:
   """
   A generic class to represent C structs in python.

   This class provides a fatter interface to the python struct module. Structs
   can be defined by field, with their associated struct format character. A
   simple example:

      p = cStruct( ('h', 'shortid'), ('l', 'longnum') )
      p.shortid = 2
      p.longnum = 10e6
      print repr(p.pack())
   """
   def __init__(self, fields):
      _fields  = []
      _formats = {}
      _values  = {}

      for f in fields:
         _fields.append(f[1])
         _formats[f[1]] = f[0]
         if len(f) == 3:
            _values[f[1]] = f[2]
         else:
            _values[f[1]] = 0

      self.__dict__['_fields']  = _fields
      self.__dict__['_formats'] = _formats
      self.__dict__['_values']  = _values

   def __str__(self):
      return '<cStruct: %s>' % ', '.join(['%s=%s' % x for x in self._values.iteritems()])

   def __getattr__(self, a):
      return self._values.get(a)

   def __setattr__(self, a, val):
      self._values[a] = val

   def __eq__(self, other):
      return self._values == other._values

   def unpack(self, datastr):
      pos = 0
      if len(datastr) == 0:
         return
      for f in self._fields:
         if pos > len(datastr):
            break
         fmt = self._formats[f]
         if fmt == 's':
            #print 'unpack %s AS STR' % f
            datalen = len(datastr) - pos # XXX string must be last in struct
            setattr(self, f, struct.unpack('%is' % datalen, datastr[pos:pos+datalen])[0])
         else:
            #print 'unpack %s' % f
            datalen = struct.calcsize(fmt)
            setattr(self, f, struct.unpack(fmt, datastr[pos:pos+datalen])[0])
         #print 'size %i' % datalen
         pos += datalen


   def pack(self):
      ret = ''
      for f in self._fields:
         if self._formats[f] == 's':
            if self._values[f]: #XXX - no string = no data
               ret += struct.pack('%is' % len(self._values[f]), self._values[f])
         else:
            ret += struct.pack(self._formats[f], self._values[f])
      return ret

