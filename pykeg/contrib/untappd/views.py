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
from socialregistration.clients.oauth import OAuthError
from pykeg.web.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext

from . import forms
from . import oauth_client


@staff_member_required
def admin_settings(request, plugin):
    context = RequestContext(request)
    settings_form = plugin.get_site_settings_form()

    if request.method == 'POST':
        if 'submit-settings' in request.POST:
            settings_form = forms.SiteSettingsForm(request.POST)
            if settings_form.is_valid():
                plugin.save_site_settings_form(settings_form)
                messages.success(request, 'Settings updated')

    context['plugin'] = plugin
    context['settings_form'] = settings_form

    return render_to_response('contrib/untappd/untappd_admin_settings.html',
        context_instance=context)


@login_required
def user_settings(request, plugin):
    context = RequestContext(request)
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

    return render_to_response('contrib/untappd/untappd_user_settings.html',
        context_instance=context)


@login_required
def auth_redirect(request):
    if 'submit-remove' in request.POST:
        plugin = request.plugins.get('untappd')
        plugin.save_user_profile(request.user, None)
        plugin.save_user_token(request.user, '')
        messages.success(request, 'Removed Untappd account.')
        return redirect('account-plugin-settings', plugin_name='untappd')

    plugin = request.plugins['untappd']
    url = request.build_absolute_uri(reverse('plugin-untappd-callback'))
    client = get_client(*plugin.get_credentials(), callback_url=url)

    request.session['untappd_client'] = client

    try:
        return redirect(client.get_redirect_url())
    except OAuthError, error:
        messages.error(request, 'Error: %s' % str(error))
        return redirect('account-plugin-settings', plugin_name='untappd')


@login_required
def auth_callback(request):
    try:
        client = request.session['untappd_client']
        del request.session['untappd_client']
        token = client.complete(dict(request.GET.items()))
    except KeyError:
        messages.error(request, 'Session expired.')
    except OAuthError, error:
        messages.error(request, str(error))
    else:
        plugin = request.plugins.get('untappd')
        profile = client.get_user_info()
        token = client.get_access_token()
        plugin.save_user_profile(request.user, profile)
        plugin.save_user_token(request.user, token)

        username = '%s %s' % (profile.get('first_name'), profile.get('last_name'))
        messages.success(request, 'Successfully linked to Untappd user %s' % username)

    return redirect('account-plugin-settings', plugin_name='untappd')


def get_client(client_id, client_secret, callback_url):
    client = oauth_client.Untappd(callback_url=callback_url)
    client.client_id = client_id
    client.secret = client_secret
    return client
