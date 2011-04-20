# Copyright 2011 Mike Wakerly <opensource@hoho.com>
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

from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.http import HttpResponseRedirect

class KegbotSiteMiddleware:
  def process_request(self, request):
    if not hasattr(request, 'kbsite'):
      sitename = 'default'
      try:
        request.kbsite = models.KegbotSite.objects.get(name=sitename)
      except models.KegbotSite.DoesNotExist:
        request.kbsite = None

class SiteActiveMiddleware:
  """Middleware which throws 503s when KegbotSite.is_active is false."""
  ALLOWED_PATHS = (
      '/accounts/login/',
      '/admin/',
      '/site_media/',
  )
  def _path_allowed(self, path):
    for p in self.ALLOWED_PATHS:
      if path.startswith(p):
        return True
    return False

  def process_request(self, request):
    kbsite = None
    if hasattr(request, 'kbsite'):
      kbsite = request.kbsite

    # We have a KegbotSite, and that site is active: nothing to do.
    if kbsite and kbsite.is_active:
      return None

    # If the request is for a whitelisted path, allow it.
    if self._path_allowed(request.path):
      return None

    # Allow staff/superusers access if inactive.
    if request.user.is_staff or request.user.is_superuser:
      return None
    else:
      return HttpResponse('Site temporarily unavailable', status=503)
