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

"""Kegweb RESTful API views."""

import sys

# Use simplejson if python version is < 2.6
if sys.version_info[:2] < (2, 6):
  import simplejson as json
else:
  import json


from django.conf import settings
from django.http import HttpResponse

from pykeg.core import models
from pykeg.core import protolib
from kegweb.kegweb import view_util

INDENT = 0
if settings.DEBUG:
  INDENT = 2

def ToJsonError(e):
  # TODO(mikey): add api-specific exceptions with more helpful error messages.
  return {'error_code': 500, 'error_message': str(e)}

def jsonhandler(f, full=False):
  """Decorator which translates function response to JSON.

  The wrapped function should return either a single Django model instance, or
  an iterable of the same.

  This is a bit roundabount and inefficient:  Django model instances are first
  converted to protocol buffers, then to base python types, and finally to a
  JSON-formatted string.

  TODO(mikey): revisit this layering as the API matures, or once a kegbot site
  needs to handle >0.1 qps :)
  """
  def new_function(*args, **kwargs):
    try:
      res = f(*args, **kwargs)
      request = args[0]
      with_full = full
      if request.GET.get('full') == '1':
        with_full = True
      if hasattr(res, '__iter__'):
        res = [protolib.ProtoMessageToDict(protolib.ToProto(x, with_full)) for x in res]
        res = {'result': res}
      else:
        res = protolib.ProtoMessageToDict(protolib.ToProto(res, with_full))
    except ValueError, e:
      res = ToJsonError(e)
    return HttpResponse(json.dumps(res, indent=INDENT),
        mimetype='application/json')
  return new_function

@jsonhandler
def last_drinks(request):
  return view_util.all_valid_drinks().order_by('-endtime')[:10]

@jsonhandler
def all_kegs(request):
  return models.Keg.objects.all().order_by('-startdate')

@jsonhandler
def all_drinks(request):
  return models.Drink.objects.all().order_by('id')

@jsonhandler
def all_taps(request):
  return models.KegTap.objects.all().order_by('name')

