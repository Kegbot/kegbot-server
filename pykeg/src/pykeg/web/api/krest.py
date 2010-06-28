# Copyright 2010 Mike Wakerly <opensource@hoho.com>
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

"""Kegweb API client."""

import sys

from pykeg import settings
from pykeg.core import models_pb2
from pykeg.core.protoutil import DictToProtoMessage

try:
  from urllib.parse import urlencode
  from urllib.request import urlopen
  from urllib.error import URLError
except ImportError:
  from urllib import urlencode
  from urllib2 import urlopen
  from urllib2 import URLError

try:
  import json
except ImportError:
  try:
    import simplejson as json
  except ImportError:
    import django.utils.simplejson as json

import gflags
FLAGS = gflags.FLAGS

_DEFAULT_URL = ''
if hasattr(settings, 'KEGWEB_BASE_URL'):
  _DEFAULT_URL = '%s/api' % getattr(settings, 'KEGWEB_BASE_URL')

gflags.DEFINE_string('krest_url', _DEFAULT_URL,
    'Base URL for the Kegweb HTTP api.')


class KrestClient:
  """Kegweb RESTful API client."""
  def __init__(self, base_url=None):
    if not base_url:
      base_url = FLAGS.krest_url
    self._base_url = base_url

  def request(self, endpoint, **kwargs):
    if 'full' in kwargs:
      if kwargs['full'] != 0:
        kwargs['full'] = 1
    else:
      kwargs['full'] = 1

    url = '%s/%s' % (self._base_url, endpoint)
    args = urlencode(kwargs)

    full_url = '%s?%s' % (url, args)

    try:
      response = urlopen(full_url).read()
    except URLError, e:
      raise IOError('Server error: %s' % e)
    return json.loads(response)['result']

  def _DictListToProtoList(self, d_list, proto_obj):
    return (DictToProtoMessage(m, proto_obj) for m in d_list)

  def TapStatus(self, full=True):
    """Gets the status of all taps."""
    response = self.request('all-taps', full=full)
    return self._DictListToProtoList(response, models_pb2.KegTap())

  def LastDrinks(self, full=True):
    """Gets a list of the most recent drinks."""
    response = self.request('last-drinks', full=full)
    return self._DictListToProtoList(response, models_pb2.Drink())

  def AllDrinks(self, full=True):
    """Gets a list of all drinks."""
    response = self.request('all-drinks', full=full)
    return self._DictListToProtoList(response, models_pb2.Drink())


def main():
  c = KrestClient()

  print '== tap status =='
  for t in c.TapStatus():
    print t
    print ''

  print '== last drinks =='
  for d in c.LastDrinks():
    print d
    print ''

if __name__ == '__main__':
  FLAGS(sys.argv)
  main()
