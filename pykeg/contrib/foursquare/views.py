from builtins import str
from django.contrib import messages
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from pykeg.web.decorators import staff_member_required
from pykeg.util import kbjson

from . import forms
from . import client


@staff_member_required
def admin_settings(request, plugin):
    context = {}
    settings_form = plugin.get_site_settings_form()

    if request.method == "POST":
        if "submit-settings" in request.POST:
            settings_form = forms.SiteSettingsForm(request.POST)
            if settings_form.is_valid():
                plugin.save_site_settings_form(settings_form)

                venue_id = settings_form.cleaned_data.get("venue_id")
                venue = None
                if venue_id:
                    c = plugin.get_client()
                    try:
                        venue = c.venues(venue_id)
                    except client.FoursquareClientError as e:
                        messages.error(request, "Error fetching venue information: %s" % str(e))
                plugin.save_venue_detail(venue)
                messages.success(request, "Settings updated.")

        if "test-api" in request.POST:
            plugin = request.plugins["foursquare"]
            c = plugin.get_client()
            venue_id = plugin.get_venue_id() or "49d01698f964a520fd5a1fe3"  # Golden Gate Bridge
            try:
                venue_info = c.venues(venue_id)
                context["test_response"] = kbjson.dumps(venue_info, indent=2)
                messages.success(request, "API test successful.")
            except client.FoursquareClientError as e:
                messages.success(request, "API test failed: {}".format(e))

    context["plugin"] = plugin
    context["settings_form"] = settings_form
    context["venue_detail"] = plugin.get_venue_detail()

    return render(request, "contrib/foursquare/foursquare_admin_settings.html", context=context)


@login_required
def user_settings(request, plugin):
    context = {}
    user = request.user

    settings_form = plugin.get_user_settings_form(user)

    if request.method == "POST":
        if "submit-settings" in request.POST:
            settings_form = forms.UserSettingsForm(request.POST)
            if settings_form.is_valid():
                plugin.save_user_settings_form(user, settings_form)
                messages.success(request, "Settings updated")

    context["plugin"] = plugin
    context["venue"] = plugin.get_venue_detail()
    context["profile"] = plugin.get_user_profile(user)
    context["settings_form"] = settings_form

    return render(request, "contrib/foursquare/foursquare_user_settings.html", context=context)


@login_required
def auth_redirect(request):
    if "submit-remove" in request.POST:
        plugin = request.plugins.get("foursquare")
        plugin.save_user_profile(request.user, None)
        plugin.save_user_token(request.user, "")
        messages.success(request, "Removed Foursquare account.")
        return redirect("account-plugin-settings", plugin_name="foursquare")

    plugin = request.plugins["foursquare"]
    client = plugin.get_client()
    redirect_url = request.build_absolute_uri(reverse("plugin-foursquare-callback"))
    url = client.get_authorization_url(redirect_url)
    return redirect(url)


@login_required
def auth_callback(request):
    plugin = request.plugins["foursquare"]
    client = plugin.get_client()
    code = request.GET.get("code")
    redirect_url = request.build_absolute_uri(reverse("plugin-foursquare-callback"))
    token = client.handle_authorization_callback(code, redirect_url)

    profile = client.users(token)
    if not profile or not profile.get("user"):
        messages.error(request, "Unexpected profile response.")
    else:
        profile = profile["user"]
        plugin.save_user_profile(request.user, profile)
        plugin.save_user_token(request.user, token)

        username = "%s %s" % (profile.get("firstName"), profile.get("lastName"))
        messages.success(request, "Successfully linked to foursquare user %s" % username)

    return redirect("account-plugin-settings", plugin_name="foursquare")
