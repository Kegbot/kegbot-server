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

from pykeg import EPOCH

from pykeg.core import models
from pykeg.core.backend import KegbotBackend

from django.db import DatabaseError
from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.http import Http404
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import SimpleTemplateResponse
from django.template import RequestContext

# TODO(mikey): rename me
ALLOWED_PATHS = (
    '/api/login/',
    '/api/get-api-key/',
    '/accounts/login/',
    '/admin/',
    '/media/',
    '/setup/',
)

def _path_allowed(path, kbsite):
  for p in ALLOWED_PATHS:
    if path.startswith(p):
      return True
  return False


class KegbotSiteMiddleware:
  ALLOWED_VIEW_MODULE_PREFIXES = (
      'pykeg.web.setup_wizard.',
  )
  def process_request(self, request):
    epoch = None
    request.need_setup = False
    request.need_upgrade = False

    try:
      request.kbsite = models.KegbotSite.objects.get(name='default')
      epoch = request.kbsite.epoch
    except (models.KegbotSite.DoesNotExist, DatabaseError), e:
      request.kbsite = None

    if not request.kbsite or not request.kbsite.is_setup:
      request.need_setup = True
    elif not epoch or epoch < EPOCH:
      request.need_upgrade = True

    request.backend = KegbotBackend()
    return None

  def process_view(self, request, view_func, view_args, view_kwargs):
    for prefix in self.ALLOWED_VIEW_MODULE_PREFIXES:
      if view_func.__module__.startswith(prefix):
        return None

    if request.need_setup:
      return self._setup_required(request)
    elif request.need_upgrade:
      return self._upgrade_required(request)

    return None

  def _setup_required(self, request):
    return SimpleTemplateResponse('setup_wizard/setup_required.html',
        context=RequestContext(request), status=403)

  def _upgrade_required(self, request, current_epoch=None):
    context = RequestContext(request)
    context['current_epoch'] = current_epoch
    return SimpleTemplateResponse('setup_wizard/upgrade_required.html',
        context=context, status=403)


class SiteActiveMiddleware:
  """Middleware which throws 503s when KegbotSite.is_active is false."""
  def process_view(self, request, view_func, view_args, view_kwargs):
    if not hasattr(request, 'kbsite') or not request.kbsite:
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

class HttpHostMiddleware:
  """Middleware which checks a dynamic version of settings.ALLOWED_HOSTS."""
  def process_request(self, request):
    if not getattr(request, 'kbsite', None):
      return None

    host = request.get_host()
    allowed_hosts_str = request.kbsite.settings.allowed_hosts
    if allowed_hosts_str:
      host_patterns = allowed_hosts_str.strip().split()
    else:
      host_patterns = []
    valid = HttpHostMiddleware.validate_host(host, host_patterns)

    if not valid:
      message =  "Invalid HTTP_HOST header (you may need to change Kegbot's ALLOWED_HOSTS setting): %s" % host
      if request.user.is_superuser or request.user.is_staff:
        messages.warning(request, message)
      else:
        raise SuspiciousOperation(message)

  @classmethod
  def validate_host(cls, host, allowed_hosts):
    """Clone of django.http.request.validate_host.

    Local differences: treats an empty `allowed_hosts` list as a pass.
    """
    # Validate only the domain part.
    if not allowed_hosts:
      return True

    if host[-1] == ']':
        # It's an IPv6 address without a port.
        domain = host
    else:
        domain = host.rsplit(':', 1)[0]

    for pattern in allowed_hosts:
      pattern = pattern.lower()
      match = (
          pattern == '*' or
          pattern.startswith('.') and (
              domain.endswith(pattern) or domain == pattern[1:]
              ) or
          pattern == domain
          )
      if match:
          return True

    return False


class PrivacyMiddleware:
  """Enforces site privacy settings.

  Must be installed after ApiRequestMiddleware (in request order) to
  access is_kb_api_request attribute.
  """
  def process_view(self, request, view_func, view_args, view_kwargs):
    if not hasattr(request, 'kbsite'):
      return None
    elif _path_allowed(request.path, request.kbsite):
      return None
    elif request.is_kb_api_request:
      # api.middleware will enforce access requirements.
      return None

    privacy = request.kbsite.settings.privacy

    if privacy == 'public':
      return None
    elif privacy == 'staff':
      if not request.user.is_staff:
        return SimpleTemplateResponse('kegweb/staff_only.html',
            context=RequestContext(request), status=401)
      return None
    elif privacy == 'members':
      if not request.user.is_authenticated or not request.user.is_active:
        return SimpleTemplateResponse('kegweb/members_only.html',
            context=RequestContext(request), status=401)
      return None

    return HttpResponse('Server misconfigured, unknown privacy setting:%s' % privacy, status=500)

