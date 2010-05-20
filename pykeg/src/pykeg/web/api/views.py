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
from django.template.loader import get_template
from django.template import Context

from pykeg.core import models
from pykeg.core import protolib
from pykeg.web.kegweb import view_util

INDENT = 0
if settings.DEBUG:
  INDENT = 2

def ToJsonError(e):
  # TODO(mikey): add api-specific exceptions with more helpful error messages.
  return {'error_code': 500, 'error_message': str(e)}

def py_to_json(f):
  def new_function(*args, **kwargs):
    try:
      result = f(*args, **kwargs)
    except ValueError, e:
      result = ToJsonError(e)
    return HttpResponse(json.dumps(result, indent=INDENT),
        mimetype='application/json')
  return new_function

class jsonhandler:
  """Decorator which translates function response to JSON.

  The wrapped function should return either a single Django model instance, or
  an iterable of the same.

  This is a bit roundabount and inefficient:  Django model instances are first
  converted to protocol buffers, then to base python types, and finally to a
  JSON-formatted string.

  TODO(mikey): revisit this layering as the API matures, or once a kegbot site
  needs to handle >0.1 qps :)
  """
  def __init__(self, func, full=False):
    self.func = func
    self.full = full

  @py_to_json
  def __call__(self, *args, **kwargs):
    res = self.func(*args, **kwargs)
    request = args[0]
    with_full = self.full
    if request.GET.get('full') == '1':
      with_full = True
    if hasattr(res, '__iter__'):
      res = [protolib.ProtoMessageToDict(protolib.ToProto(x, with_full)) for x in res]
      res = {'result': res}
    else:
      res = protolib.ProtoMessageToDict(protolib.ToProto(res, with_full))
    return res

def _get_last_drinks():
  return view_util.all_valid_drinks().order_by('-endtime')

@jsonhandler
def last_drinks(request):
  return _get_last_drinks()

@jsonhandler
def all_kegs(request):
  return models.Keg.objects.all().order_by('-startdate')

@jsonhandler
def all_drinks(request):
  return models.Drink.objects.all().order_by('id')

@jsonhandler
def all_taps(request):
  return models.KegTap.objects.all().order_by('name')

@py_to_json
def last_drinks_html(request):
  last_drinks = _get_last_drinks()

  # render each drink
  template = get_template('kegweb/drink-box.html')
  results = []
  for d in last_drinks[:10]:
    row = {}
    row['id'] = d.id
    row['box_html'] = template.render(Context({'drink': d}))
    results.append(row)
  return results

@py_to_json
def last_drink_id(request):
  last = view_util.all_valid_drinks().order_by('-endtime')
  if len(last) == 0:
    return {'id': 0}
  else:
    return {'id': last[0].id}

