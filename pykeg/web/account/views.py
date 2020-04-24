#!/usr/bin/env python
#
# Copyright 2014 Kegbot Project contributors
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
from django.urls import reverse
from django.shortcuts import render
from django.shortcuts import redirect
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST

from pykeg.core import models
from pykeg.util import email
from pykeg.web.kegweb import forms
from pykeg.notification.forms import NotificationSettingsForm


@login_required
def account_main(request):
    context = {}
    context["user"] = request.user
    return render(request, "account/index.html", context=context)


@login_required
def edit_profile(request):
    context = {}
    user = request.user

    context["form"] = forms.ProfileForm(initial={"display_name": user.get_full_name()})

    if request.method == "POST":
        form = forms.ProfileForm(request.POST, request.FILES)
        context["form"] = form
        if form.is_valid():
            if "new_mugshot" in request.FILES:
                pic = models.Picture.objects.create(user=user)
                image = request.FILES["new_mugshot"]
                pic.image.save(image.name, image)
                pic.save()
                user.mugshot = pic
            user.display_name = form.cleaned_data["display_name"]
            user.save()
    return render(request, "account/profile.html", context=context)


@login_required
def invite(request):
    context = {}
    form = forms.InvitationForm()

    if not request.kbsite.can_invite(request.user):
        raise Http404("Cannot invite from this account.")

    if request.method == "POST":
        form = forms.InvitationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            invite = models.Invitation.objects.create(for_email=email, invited_by=request.user)
            invite.send()
            messages.success(request, "Invitation mailed to " + email)

    context["form"] = form
    return render(request, "account/invite.html", context=context)


@login_required
def notifications(request):
    # TODO(mikey): Dynamically add settings forms for other e-mail
    # backends (currently hardcoded to email backend).

    context = {}
    existing_settings = models.NotificationSettings.objects.get_or_create(
        user=request.user, backend="pykeg.notification.backends.email.EmailNotificationBackend"
    )[0]

    if request.method == "POST":
        if "submit-settings" in request.POST:
            form = NotificationSettingsForm(request.POST, instance=existing_settings)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.user = request.user
                instance.backend = "pykeg.notification.backends.email.EmailNotificationBackend"
                instance.save()
                messages.success(request, "Settings updated")
                existing_settings = instance

        elif "submit-email" in request.POST:
            form = forms.ChangeEmailForm(request.POST)
            if form.is_valid():
                new_email = form.cleaned_data["email"]
                if new_email == request.user.email:
                    messages.warning(request, "E-mail address unchanged.")
                else:
                    token = email.build_email_change_token(request.user, new_email)
                    url = models.KegbotSite.get().reverse_full(
                        "account-confirm-email", args=(), kwargs={"token": token}
                    )

                    email_context = {"url": url, "site_name": request.kbsite.title}
                    message = email.build_message(
                        new_email, "registration/email_confirm_email_change.html", email_context
                    )
                    message.send()
                    messages.success(
                        request, "An e-mail confirmation has been sent to {}".format(new_email)
                    )

        else:
            messages.error(request, "Unknown request.")

    context["form"] = NotificationSettingsForm(instance=existing_settings)
    context["email_form"] = forms.ChangeEmailForm(initial={"email": request.user.email})

    return render(request, "account/notifications.html", context=context)


@login_required
def confirm_email(request, token):
    try:
        uid, new_address = email.verify_email_change_token(request.user, token)
        if uid != request.user.uid:
            messages.error(request, "E-mail confirmation does not exist for this account.")
        elif request.user.email != new_address:
            request.user.email = new_address
            request.user.save()
            messages.success(request, "E-mail address successfully changed.")
        else:
            messages.warning(request, "E-mail address unchanged.")
    except ValueError:
        messages.error(request, "That token is not valid.")

    return redirect("account-notifications")


@never_cache
def activate_account(request, activation_key):
    users = models.User.objects.filter(activation_key=activation_key)
    if users.count() != 1:
        raise Http404("No such activation key")
    user = users[0]

    assert not user.has_usable_password(), "User already has a usable password"

    form = forms.ActivateAccountForm()
    if request.method == "POST":
        form = forms.ActivateAccountForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            # Set the password and revoke the activation key.
            user.set_password(cd.get("password"))
            user.activation_key = None
            user.save()

            # Log the user in.
            user = authenticate(username=user.username, password=cd.get("password"))
            auth_login(request, user)
            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()

            messages.success(request, "Your account has been activated!")
            return redirect("kb-account-main")

    context = {}
    context["form"] = form
    return render(request, "account/activate_account.html", context=context)


@login_required
@require_POST
def regenerate_api_key(request):
    form = forms.RegenerateApiKeyForm(request.POST)
    if form.is_valid():
        key, is_new = models.ApiKey.objects.get_or_create(user=request.user)
        key.regenerate()
        key.save()
    return redirect("kb-account-main")


@login_required
def plugin_settings(request, plugin_name):
    plugin = request.plugins.get(plugin_name, None)
    if not plugin:
        raise Http404('Plugin "%s" not loaded' % plugin_name)

    view = plugin.get_user_settings_view()
    if not view:
        raise Http404("No user settings for this plugin")

    return view(request, plugin)
