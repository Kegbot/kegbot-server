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

from builtins import str
from django.contrib import messages
from django.urls import reverse
from django.shortcuts import redirect
from pykeg.web.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from httplib2 import HttpLib2Error

from . import forms
from . import tasks

# Session keys for temporarily storing oauth client.
SESSION_KEY_SITE_TWITTER = 'site-twitter'
SESSION_KEY_USER_TWITTER = 'user-twitter'


@staff_member_required
def admin_settings(request, plugin):
    context = {}

    consumer_key, consumer_secret = plugin.get_credentials()
    initial = {
        'consumer_key': consumer_key or '',
        'consumer_secret': consumer_secret or '',
    }

    credentials_form = forms.CredentialsForm(initial=initial)
    settings_form = plugin.get_site_twitter_settings_form()
    tweet_form = forms.SendTweetForm()

    if request.method == 'POST':
        if 'submit-keys' in request.POST:
            credentials_form = forms.CredentialsForm(request.POST)
            if credentials_form.is_valid():
                consumer_key = credentials_form.cleaned_data['consumer_key']
                consumer_secret = credentials_form.cleaned_data['consumer_secret']
                plugin.set_credentials(consumer_key, consumer_secret)
                messages.success(request, 'Keys updated')

        elif 'submit-settings' in request.POST:
            settings_form = forms.SiteSettingsForm(request.POST)
            if settings_form.is_valid():
                plugin.save_form(settings_form, 'site_settings')
                messages.success(request, 'Settings updated')

        elif 'submit-tweet' in request.POST:
            tweet_form = forms.SendTweetForm(request.POST)
            if tweet_form.is_valid():
                tweet = tweet_form.cleaned_data['tweet_custom']
                consumer_key, consumer_secret = plugin.get_credentials()
                profile = plugin.get_site_profile()
                if consumer_key and consumer_secret and profile:
                    oauth_token = profile.get('oauth_token')
                    oauth_token_secret = profile.get('oauth_token_secret')
                    tasks.send_tweet(consumer_key, consumer_secret, oauth_token, oauth_token_secret,
                                     tweet, image_url=None)
                    messages.success(request, 'Tweet sent')
                else:
                    messages.error(request, 'There was a problem sending tweet')

    context['have_credentials'] = consumer_key and consumer_secret
    context['plugin'] = plugin
    context['site_profile'] = plugin.get_site_profile()
    context['credentials_form'] = credentials_form
    context['settings_form'] = settings_form
    context['tweet_form'] = tweet_form

    return render(request, 'contrib/twitter/admin_settings.html', context=context)


@login_required
def user_settings(request, plugin):
    context = {}
    user = request.user

    consumer_key, consumer_secret = plugin.get_credentials()

    settings_form = plugin.get_user_settings_form(user)

    if request.method == 'POST':
        if 'submit-settings' in request.POST:
            settings_form = forms.UserSettingsForm(request.POST)
            if settings_form.is_valid():
                plugin.save_user_settings_form(user, settings_form)
                messages.success(request, 'Settings updated')

    context['have_credentials'] = consumer_key and consumer_secret
    context['plugin'] = plugin
    context['profile'] = plugin.get_user_profile(user)
    context['settings_form'] = settings_form

    return render(request, 'contrib/twitter/twitter_user_settings.html', context=context)


@staff_member_required
def site_twitter_redirect(request):
    if 'submit-remove' in request.POST:
        plugin = request.plugins.get('twitter')
        plugin.remove_site_profile()
        messages.success(request, 'Removed Twitter account.')
        return redirect('kegadmin-plugin-settings', plugin_name='twitter')

    return do_redirect(request, 'plugin-twitter-site_twitter_callback', 'kegadmin-plugin-settings', SESSION_KEY_SITE_TWITTER)


@staff_member_required
def site_twitter_callback(request):
    plugin = request.plugins.get('twitter')
    try:
        resource_owner_key, resource_owner_secret = request.session.get(SESSION_KEY_SITE_TWITTER, [])
    except ValueError:
        messages.error(request, 'Lost session, please try again.')
    else:
        client = plugin.get_client()
        del request.session[SESSION_KEY_SITE_TWITTER]
        token, token_secret = client.handle_authorization_callback(resource_owner_key, resource_owner_secret, request)
        user_info = client.get_user_info(token, token_secret)
        plugin.save_site_profile(token, token_secret, user_info.screen_name, user_info.id)
        messages.success(request, 'Successfully linked to @%s' % user_info.screen_name)

    return redirect('kegadmin-plugin-settings', plugin_name='twitter')


@login_required
def user_twitter_redirect(request):
    if 'submit-remove' in request.POST:
        plugin = request.plugins.get('twitter')
        plugin.remove_user_profile(request.user)
        messages.success(request, 'Removed Twitter account.')
        return redirect('account-plugin-settings', plugin_name='twitter')

    return do_redirect(request, 'plugin-twitter-user_twitter_callback', 'account-plugin-settings', SESSION_KEY_USER_TWITTER)


@login_required
def user_twitter_callback(request):
    plugin = request.plugins['twitter']
    try:
        resource_owner_key, resource_owner_secret = request.session.get(SESSION_KEY_USER_TWITTER, [])
    except ValueError:
        messages.error(request, 'Lost session, please try again.')
    else:
        client = plugin.get_client()
        del request.session[SESSION_KEY_USER_TWITTER]
        token, token_secret = client.handle_authorization_callback(resource_owner_key, resource_owner_secret, request)
        user_info = client.get_user_info(token, token_secret)
        plugin.save_user_profile(request.user, token, token_secret, user_info.screen_name, user_info.id)
        messages.success(request, 'Successfully linked to @%s' % user_info.screen_name)

    return redirect('account-plugin-settings', plugin_name='twitter')


def do_redirect(request, callback_url_name, next_url_name, session_key):
    """Common redirect method, handling any incidental errors.

    Args:
        request: the incoming request
        client: the TwitterClient context
        next_url_name: Django URL name to redirect to upon error

    Returns:
        A redirect response, either to the OAuth redirect URL
        or to `next_url_name` on error.
    """
    callback_url = request.build_absolute_uri(reverse(callback_url_name))
    client = request.plugins['twitter'].get_client()

    url, resource_owner_key, resource_owner_secret = client.get_redirect_url(callback_url)
    request.session[session_key] = (resource_owner_key, resource_owner_secret)

    try:
        return redirect(url)
    except HttpLib2Error as e:
        # This path can occur when api.twitter.com is unresolvable
        # or unreachable.
        messages.error(request, 'Twitter API server not available. Try again later. (%s)' % str(e))
        return redirect(next_url_name, plugin_name='twitter')
