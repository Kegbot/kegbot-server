#!/usr/bin/env python
#
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

"""Kegweb main views."""

from django.http import Http404
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.template import RequestContext
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST
from django.contrib.auth.views import password_change as password_change_orig
from django.contrib.auth.views import password_change_done as password_change_done_orig

from pykeg.core import models
from pykeg.web.kegweb import forms
from pykeg.notification.forms import NotificationSettingsForm


@login_required
def account_main(request):
    context = RequestContext(request)
    context['user'] = request.user
    return render_to_response('account/index.html', context_instance=context)


@login_required
def edit_profile(request):
    context = RequestContext(request)
    user = request.user

    context['form'] = forms.ProfileForm(initial={'display_name': user.get_full_name()})

    if request.method == 'POST':
        form = forms.ProfileForm(request.POST, request.FILES)
        context['form'] = form
        if form.is_valid():
            if 'new_mugshot' in request.FILES:
                pic = models.Picture.objects.create(user=user)
                image = request.FILES['new_mugshot']
                pic.image.save(image.name, image)
                pic.save()
                user.mugshot = pic
            user.display_name = form.cleaned_data['display_name']
            user.save()
    return render_to_response('account/profile.html', context_instance=context)


@login_required
def invite(request):
    context = RequestContext(request)
    form = forms.InvitationForm()

    if not request.kbsite.can_invite(request.user):
        raise Http404('Cannot invite from this account.')

    if request.method == 'POST':
        form = forms.InvitationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            invite = models.Invitation.objects.create(for_email=email,
                invited_by=request.user)
            invite.send()
            messages.success(request, 'Invitation mailed to ' + email)

    context['form'] = form
    return render_to_response('account/invite.html', context_instance=context)


@login_required
def notifications(request):
    # TODO(mikey): Dynamically add settings forms for other e-mail
    # backends (currently hardcoded to email backend).
    context = RequestContext(request)
    existing_settings = models.NotificationSettings.objects.get_or_create(user=request.user,
        backend='pykeg.notification.backends.email.EmailNotificationBackend')[0]
    if request.method == 'POST':
        form = NotificationSettingsForm(request.POST, instance=existing_settings)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.backend = 'pykeg.notification.backends.email.EmailNotificationBackend'
            instance.save()
            messages.success(request, 'Settings updated')
            existing_settings = instance
    context['form'] = NotificationSettingsForm(instance=existing_settings)
    return render_to_response('account/notifications.html', context_instance=context)


@never_cache
def activate_account(request, activation_key):
    users = models.User.objects.filter(activation_key=activation_key)
    if users.count() != 1:
        raise Http404('No such activation key')
    user = users[0]

    assert not user.has_usable_password(), 'User already has a usable password'

    form = forms.ActivateAccountForm()
    if request.method == 'POST':
        form = forms.ActivateAccountForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            # Set the password and revoke the activation key.
            user.set_password(cd.get('password'))
            user.activation_key = None
            user.save()

            # Log the user in.
            user = authenticate(username=user.username, password=cd.get('password'))
            auth_login(request, user)
            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()

            messages.success(request, 'Your account has been activated!')
            return redirect('kb-account-main')

    context = RequestContext(request)
    context['form'] = form
    return render_to_response('account/activate_account.html', context_instance=context)


@login_required
@require_POST
def regenerate_api_key(request):
    form = forms.RegenerateApiKeyForm(request.POST)
    if form.is_valid():
        key, is_new = models.ApiKey.objects.get_or_create(user=request.user)
        key.regenerate()
        key.save()
    return redirect('kb-account-main')


def password_change(request, *args, **kwargs):
    kwargs['template_name'] = 'account/password_change.html'
    kwargs['post_change_redirect'] = reverse('password_change_done')
    return password_change_orig(request, *args, **kwargs)


def password_change_done(request):
    return password_change_done_orig(request, 'account/password_change_done.html')


@login_required
def plugin_settings(request, plugin_name):
    plugin = request.plugins.get(plugin_name, None)
    if not plugin:
        raise Http404('Plugin "%s" not loaded' % plugin_name)

    view = plugin.get_user_settings_view()
    if not view:
        raise Http404('No user settings for this plugin')

    return view(request, plugin)
