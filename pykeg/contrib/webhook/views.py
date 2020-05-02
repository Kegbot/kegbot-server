from django.contrib import messages
from pykeg.web.decorators import staff_member_required
from django.shortcuts import render

from . import forms


@staff_member_required
def admin_settings(request, plugin):
    context = {}
    settings_form = plugin.get_site_settings_form()

    if request.method == "POST":
        if "submit-settings" in request.POST:
            settings_form = forms.SiteSettingsForm(request.POST)
            if settings_form.is_valid():
                plugin.save_site_settings_form(settings_form)
                messages.success(request, "Settings updated")

    context["plugin"] = plugin
    context["settings_form"] = settings_form

    return render(request, "contrib/webhook/webhook_admin_settings.html", context=context)
