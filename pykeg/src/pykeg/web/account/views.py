#!/usr/bin/env python
#
# Copyright 2010 Mike Wakerly <opensource@hoho.com>
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
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic.simple import redirect_to

from pykeg.core import models
from pykeg.web.kegweb import forms
from pykeg.web.api import apikey

@login_required
def account_main(request):
  user = request.user
  context = RequestContext(request)
  form = forms.UserProfileForm(instance=user.get_profile())
  if request.method == 'POST':
    orig_profile = request.user.get_profile()
    form = forms.UserProfileForm(request.POST, instance=orig_profile)
    if form.is_valid():
      new_profile = form.save()
  context['user'] = user
  context['profile_form'] = form
  return render_to_response('account/index.html', context)

@login_required
def edit_mugshot(request):
  context = RequestContext(request)
  context['mugshot_form'] = forms.MugshotForm()
  if request.method == 'POST':
    form = forms.MugshotForm(request.POST, request.FILES)
    context['mugshot_form'] = form
    if form.is_valid():
      pic = models.Picture.objects.create(user=request.user)
      image = request.FILES['new_mugshot']
      pic.image.save(image.name, image)
      pic.save()

      profile = request.user.get_profile()
      profile.mugshot = pic
      profile.save()
  return render_to_response('account/mugshot.html', context)

@login_required
def regenerate_api_key(request):
  if request.method != 'POST':
    raise Http404
  form = forms.RegenerateApiKeyForm(request.POST)
  if form.is_valid():
    profile = request.user.get_profile()
    profile.api_secret = apikey.ApiKey.NewSecret()
    profile.save()
  return redirect_to(request, url='/account')

