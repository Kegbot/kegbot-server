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

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from pykeg.web.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from . import forms


@staff_member_required
def admin_settings(request, plugin):
    context = {}
    settings_form = plugin.get_site_settings_form()

    if request.method == 'POST':
        if 'submit-settings' in request.POST:
            settings_form = forms.SiteSettingsForm(request.POST)
            if settings_form.is_valid():
                plugin.save_site_settings_form(settings_form)
                messages.success(request, 'Settings updated')

    context['plugin'] = plugin
    context['settings_form'] = settings_form

    return render(request, 'contrib/untappd/untappd_admin_settings.html',
                  context=context)


@login_required
def user_settings(request, plugin):
    context = {}
    user = request.user

    settings_form = plugin.get_user_settings_form(user)

    if request.method == 'POST':
        if 'submit-settings' in request.POST:
            settings_form = forms.UserSettingsForm(request.POST)
            if settings_form.is_valid():
                plugin.save_user_settings_form(user, settings_form)
                messages.success(request, 'Settings updated')

    context['plugin'] = plugin
    context['profile'] = plugin.get_user_profile(user)
    context['settings_form'] = settings_form

    return render(request, 'contrib/untappd/untappd_user_settings.html',
                  context=context)


@login_required
def auth_redirect(request):
    if 'submit-remove' in request.POST:
        plugin = request.plugins.get('untappd')
        plugin.save_user_profile(request.user, None)
        plugin.save_user_token(request.user, '')
        messages.success(request, 'Removed Untappd account.')
        return redirect('account-plugin-settings', plugin_name='untappd')

    plugin = request.plugins['untappd']
    client = plugin.get_client()
    callback_url = request.build_absolute_uri(reverse('plugin-untappd-callback'))
    url, state = client.get_authorization_url(callback_url)
    return redirect(url)


@login_required
def auth_callback(request):
    plugin = request.plugins['untappd']
    client = plugin.get_client()

    callback_url = request.build_absolute_uri(reverse('plugin-untappd-callback'))
    result = client.handle_authorization_callback(request.build_absolute_uri(), callback_url)
    token = result['access_token']

    profile = client.get_user_info(token)
    username = profile['user_name']
    plugin.save_user_profile(request.user, profile)
    plugin.save_user_token(request.user, token)

    messages.success(request, 'Successfully linked to Untappd user %s' % username)
    return redirect('account-plugin-settings', plugin_name='untappd')
