# Copyright 2012 Mike Wakerly <opensource@hoho.com>
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

from pykeg.core import models
from pykeg.web.api import util as apiutil

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.http import Http404
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import SimpleTemplateResponse
from django.template import RequestContext

ALLOWED_PATHS = (
    '/api/login/',
    '/api/get-api-key/',
    '/accounts/login/',
    '/admin/',
    '/media/',
    '/setup/',
)

def _path_allowed(path, kbsite):
  if kbsite:
    path = path.lstrip(kbsite.url())
  for p in ALLOWED_PATHS:
    if path.startswith(p):
      return True
  return False


class KegbotSiteMiddleware:
  ALLOWED_VIEW_MODULE_PREFIXES = (
      'pykeg.web.setup_wizard.',
  )
  def process_view(self, request, view_func, view_args, view_kwargs):
    """Removes kbsite_name from kwargs if present, and attaches the
    corresponding KegbotSite instance to the request as the "kbsite" attribute.

    If kbsite_name is None, the default site is selected.
    """
    kbsite_name = view_kwargs.pop('kbsite_name', None)
    if not kbsite_name:
      kbsite_name = 'default'
    request.kbsite_name = kbsite_name
    try:
      request.kbsite = models.KegbotSite.objects.get(name=kbsite_name)
    except models.KegbotSite.DoesNotExist:
      request.kbsite = None

    if not request.kbsite.is_setup:
      module = view_func.__module__
      allowed = False
      for prefix in self.ALLOWED_VIEW_MODULE_PREFIXES:
        if module.startswith(prefix):
          allowed = True
          break
      if not allowed:
        return SimpleTemplateResponse('setup_wizard/setup_required.html',
            context=RequestContext(request), status=403)
    return None


class SiteActiveMiddleware:
  """Middleware which throws 503s when KegbotSite.is_active is false."""
  def process_view(self, request, view_func, view_args, view_kwargs):
    if not hasattr(request, 'kbsite'):
      return None
    kbsite = request.kbsite

    # We have a KegbotSite, and that site is active: nothing to do.
    if kbsite.is_active:
      return None

    # If the request is for a whitelisted path, allow it.
    if _path_allowed(request.path, kbsite):
      return None

    # Allow staff/superusers access if inactive.
    if request.user.is_staff or request.user.is_superuser:
      return None

    return HttpResponse('Site temporarily unavailable', status=503)


class PrivacyMiddleware:
  """Enforces site privacy settings."""
  def process_view(self, request, view_func, view_args, view_kwargs):
    if not hasattr(request, 'kbsite'):
      return None
    elif _path_allowed(request.path, request.kbsite):
      return None
    elif apiutil.request_is_authenticated(request):
      # This is an auth-required kb api view; no need to check privacy since API
      # keys are given staff-level access.
      return None

    privacy = request.kbsite.settings.privacy
    if privacy == 'public':
      return None

    # If non-public, apply the API key check.
    if apiutil.is_api_view(view_func):
      try:
        apiutil.check_api_key(request)
        return
      except Exception, e:
        return apiutil.wrap_exception(request, e)

    if privacy == 'staff' and not request.user.is_staff:
      return SimpleTemplateResponse('kegweb/staff_only.html',
          context=RequestContext(request), status=401)
    elif privacy == 'members':
      if not request.user.is_authenticated or not request.user.is_active:
        return SimpleTemplateResponse('kegweb/members_only.html',
            context=RequestContext(request), status=401)
      return None

    return HttpResponse('Server misconfigured, unknown privacy setting:%s' % privacy, status=500)

