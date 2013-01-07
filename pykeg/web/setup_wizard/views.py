# Copyright 2013 Mike Wakerly <opensource@hoho.com>
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

from functools import wraps
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.cache import never_cache
from django.views.generic.simple import redirect_to

from .forms import AdminUserForm
from .forms import MiniSiteSettingsForm

def setup_view(f):
  """Decorator for setup views."""
  def new_function(*args, **kwargs):
    request = args[0]
    if request.kbsite and request.kbsite.is_setup:
      if not request.user.is_active or not request.user.is_admin:
        raise Http404('Admin user is required to modify existing site.')
    return f(*args, **kwargs)
  return wraps(f)(new_function)

@setup_view
@never_cache
def start(request):
  context = RequestContext(request)
  return render_to_response('setup_wizard/start.html', context)

@setup_view
@never_cache
def site_settings(request):
  context = RequestContext(request)
  form = MiniSiteSettingsForm(instance=request.kbsite.settings)
  if request.method == 'POST':
    form = MiniSiteSettingsForm(request.POST, instance=request.kbsite.settings)
    if form.is_valid():
      form.save()
      messages.success(request, 'Settings saved!')
      result_url = reverse('setup_admin', args=[request.kbsite.url()])
      return redirect_to(request, result_url)
  context['form'] = form
  return render_to_response('setup_wizard/site_settings.html', context)

@setup_view
@never_cache
def admin(request):
  context = RequestContext(request)
  form = AdminUserForm()
  if request.method == 'POST':
    form = AdminUserForm(request.POST)
    if form.is_valid():
      form.save()
      user = authenticate(username=form.cleaned_data.get('username'),
          password=form.cleaned_data.get('password'))
      if user:
        login(request, user)
      result_url = reverse('setup_finish', args=[request.kbsite.url()])
      return redirect_to(request, result_url)
  context['form'] = form
  return render_to_response('setup_wizard/admin.html', context)

@setup_view
@never_cache
def finish(request):
  context = RequestContext(request)
  if request.method == 'POST':
    request.kbsite.is_setup = True
    request.kbsite.save()
    messages.success(request, 'Tip: Install a new Keg in Admin: Taps')
    result_url = reverse('kb-home', args=[request.kbsite.url()])
    return redirect_to(request, result_url)
  return render_to_response('setup_wizard/finish.html', context)
