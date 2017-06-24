# Copyright 2014 Bevbot LLC, All Rights Reserved
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
from django.http import Http404
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.decorators.cache import never_cache

from pykeg.core import defaults
from pykeg.core import models

from .forms import AdminUserForm
from .forms import MiniSiteSettingsForm


def setup_view(f):
    """Decorator for setup views."""
    def new_function(*args, **kwargs):
        request = args[0]
        if not settings.DEBUG:
            raise Http404('Site is not in DEBUG mode.')
        if request.kbsite and request.kbsite.is_setup:
            raise Http404('Site is already setup, wizard disabled.')
        return f(*args, **kwargs)
    return wraps(f)(new_function)


@setup_view
@never_cache
def start(request):
    """ Shows the enable/disable hardware toggle. """
    context = {}

    if request.method == 'POST':
        if 'enable_sensing' in request.POST:
            request.session['enable_sensing'] = True
            return redirect('setup_accounts')
        elif 'disable_sensing' in request.POST:
            request.session['enable_sensing'] = False
            request.session['enable_users'] = False
            return redirect('setup_site_settings')
        else:
            messages.error(request, 'Unknown response.')

    return render(request, 'setup_wizard/start.html', context=context)


@setup_view
@never_cache
def setup_accounts(request):
    """ Shows the enable/disable accounts toggle. """
    context = {}

    if request.method == 'POST':
        if 'enable_users' in request.POST:
            request.session['enable_users'] = True
            return redirect('setup_site_settings')
        elif 'disable_users' in request.POST:
            request.session['enable_users'] = False
            return redirect('setup_site_settings')
        else:
            messages.error(request, 'Unknown response.')

    return render(request, 'setup_wizard/accounts.html', context=context)


@setup_view
@never_cache
def site_settings(request):
    context = {}

    if request.method == 'POST':
        form = MiniSiteSettingsForm(request.POST, instance=request.kbsite)
        if form.is_valid():
            form.save()
            messages.success(request, 'Settings saved!')
            return redirect('setup_admin')
    else:
        try:
            defaults.set_defaults()
        except defaults.AlreadyInstalledError:
            pass

        site = models.KegbotSite.get()
        site.enable_sensing = request.session['enable_sensing']
        site.enable_users = request.session['enable_users']
        site.save()
        form = MiniSiteSettingsForm(instance=site)
    context['form'] = form
    return render(request, 'setup_wizard/site_settings.html', context=context)


@setup_view
@never_cache
def admin(request):
    context = {}
    form = AdminUserForm()
    if request.method == 'POST':
        form = AdminUserForm(request.POST)
        if form.is_valid():
            form.save()
            user = authenticate(username=form.cleaned_data.get('username'),
                password=form.cleaned_data.get('password'))
            if user:
                login(request, user)
            return redirect('setup_finish')
    context['form'] = form
    return render(request, 'setup_wizard/admin.html', context=context)


@setup_view
@never_cache
def finish(request):
    context = {}
    if request.method == 'POST':
        request.kbsite.is_setup = True
        request.kbsite.save()
        messages.success(request, 'Tip: Install a new Keg in Admin: Taps')
        return redirect('kegadmin-main')
    return render(request, 'setup_wizard/finish.html', context=context)
