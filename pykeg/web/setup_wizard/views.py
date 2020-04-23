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

from functools import wraps
import logging
import traceback
from django.conf import settings
from django.core import management
from django.contrib import messages
from django.contrib.auth import authenticate
from django.http import Http404
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.decorators.cache import never_cache

from pykeg.core import defaults
from pykeg.core import models
from pykeg.util import dbstatus
from pykeg.core.util import get_version_object

from .forms import AdminUserForm
from .forms import MiniSiteSettingsForm

logger = logging.getLogger(__name__)


def setup_view(f):
    """Decorator for setup views."""

    def new_function(*args, **kwargs):
        request = args[0]
        if not settings.DEBUG:
            raise Http404("Site is not in DEBUG mode.")
        if request.kbsite and request.kbsite.is_setup:
            raise Http404("Site is already setup, wizard disabled.")
        return f(*args, **kwargs)

    return wraps(f)(new_function)


@setup_view
@never_cache
def start(request):
    """Shows database setup button"""
    context = {}

    if request.method == "POST":
        try:
            management.call_command("migrate", no_input=True)
            return redirect("setup_mode")
        except Exception as e:
            logger.exception("Error installing database")
            context["error_message"] = str(e)
            context["error_stack"] = traceback.format_exc()
    else:
        try:
            logger.info("Checking database status ...")
            dbstatus.check_db_status()
            logger.info("Database status OK.")
        except dbstatus.DatabaseNotInitialized:
            context["need_install"] = True
        except dbstatus.NeedMigration:
            context["need_upgrade"] = True

    return render(request, "setup_wizard/start.html", context=context)


@setup_view
@never_cache
def mode(request):
    """Shows the enable/disable hardware toggle."""
    context = {}

    if request.method == "POST":
        if "enable_sensing" in request.POST:
            response = redirect("setup_accounts")
            response.set_cookie("kb_setup_enable_sensing", "True")
            return response
        elif "disable_sensing" in request.POST:
            response = redirect("setup_site_settings")
            response.set_cookie("kb_setup_enable_sensing", "False")
            response.set_cookie("kb_setup_enable_users", "False")
            return response
        else:
            messages.error(request, "Unknown response.")

    return render(request, "setup_wizard/mode.html", context=context)


@setup_view
@never_cache
def upgrade(request):
    context = {}
    if request.method == "POST":
        try:
            management.call_command("migrate", no_input=True)
            site = models.KegbotSite.get()
            app_version = get_version_object()
            site.server_version = str(app_version)
            site.save()
            return redirect("kb-home")
        except Exception as e:
            logger.exception("Error installing database")
            context["error_message"] = str(e)
            context["error_stack"] = traceback.format_exc()

    try:
        logger.info("Checking database status ...")
        dbstatus.check_db_status()
        logger.info("Database status OK.")
    except dbstatus.DatabaseNotInitialized:
        context["message"] = "Database not initialized"
    except dbstatus.NeedMigration:
        context["message"] = "Database upgrade needed"

    return render(request, "setup_wizard/upgrade.html", context=context)


@setup_view
@never_cache
def setup_accounts(request):
    """ Shows the enable/disable accounts toggle. """
    context = {}

    if request.method == "POST":
        if "enable_users" in request.POST:
            response = redirect("setup_site_settings")
            response.set_cookie("kb_setup_enable_users", "True")
            return response
        elif "disable_users" in request.POST:
            response = redirect("setup_site_settings")
            response.set_cookie("kb_setup_enable_users", "False")
            return response
        else:
            messages.error(request, "Unknown response.")

    return render(request, "setup_wizard/accounts.html", context=context)


@setup_view
@never_cache
def site_settings(request):
    context = {}

    if request.method == "POST":
        site = models.KegbotSite.get()
        form = MiniSiteSettingsForm(request.POST, instance=site)
        if form.is_valid():
            form.save()
            messages.success(request, "Settings saved!")
            return redirect("setup_admin")
    else:
        try:
            defaults.set_defaults()
        except defaults.AlreadyInstalledError:
            pass

        site = models.KegbotSite.get()
        site.enable_sensing = request.COOKIES.get("kb_setup_enable_sensing") == "True"
        site.enable_users = request.COOKIES.get("kb_setup_enable_users") == "True"
        site.save()
        form = MiniSiteSettingsForm(instance=site)
    context["form"] = form
    return render(request, "setup_wizard/site_settings.html", context=context)


@setup_view
@never_cache
def admin(request):
    context = {}
    form = AdminUserForm()
    if request.method == "POST":
        form = AdminUserForm(request.POST)
        if form.is_valid():
            form.save()
            user = authenticate(
                username=form.cleaned_data.get("username"),
                password=form.cleaned_data.get("password"),
            )
            return redirect("setup_finish")
    context["form"] = form
    return render(request, "setup_wizard/admin.html", context=context)


@setup_view
@never_cache
def finish(request):
    context = {}
    if request.method == "POST":
        site = models.KegbotSite.get()
        site.is_setup = True
        site.save()
        messages.success(request, "Tip: Install a new Keg in Admin: Taps")
        return redirect("kb-home")
    return render(request, "setup_wizard/finish.html", context=context)
