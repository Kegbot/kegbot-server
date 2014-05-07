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
from pykeg.web.decorators import staff_member_required
from django.shortcuts import render_to_response
from django.template import RequestContext

from . import forms


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

    return render_to_response('contrib/webhook/webhook_admin_settings.html',
            context_instance=context)
