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

from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.shortcuts import redirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from pykeg.web.kbregistration.forms import KegbotRegistrationForm
from pykeg.backend import get_kegbot_backend

from pykeg.core import models

"""Kegbot-aware registration views."""


def register(request):
    context = RequestContext(request)
    form = KegbotRegistrationForm()

    # Check if we need an invitation before processing the request further.
    invite = None
    if request.kbsite.registration_mode != 'public':
        invite_code = None
        if 'invite_code' in request.GET:
            invite_code = request.GET['invite_code']
            request.session['invite_code'] = invite_code
        else:
            invite_code = request.session.get('invite_code', None)

        if not invite_code:
            r = render_to_response('registration/invitation_required.html',
                context_instance=context)
            r.status_code = 401
            return r

        try:
            invite = models.Invitation.objects.get(invite_code=invite_code)
        except models.Invitation.DoesNotExist:
            pass

        if not invite or invite.is_expired():
            r = render_to_response('registration/invitation_expired.html',
                context_instance=context)
            r.status_code = 401
            return r

    if request.method == 'POST':
        form = KegbotRegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data.get('password1')

            backend = get_kegbot_backend()
            backend.create_new_user(username=username, email=email, password=password)

            if invite:
                invite.delete()
                if 'invite_code' in request.session:
                    del request.session['invite_code']

            if password:
                new_user = authenticate(username=username, password=password)
                login(request, new_user)
                return redirect('kb-account-main')

            return render_to_response('registration/registration_complete.html',
                context_instance=context)

    context['form'] = form
    return render_to_response('registration/registration_form.html',
        context_instance=context)
