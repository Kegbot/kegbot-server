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
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.views.decorators.http import require_POST
from django.views.generic.simple import redirect_to

from socialregistration.contrib.foursquare import models as sr_foursquare_models
from socialregistration.contrib.twitter import models as sr_twitter_models

from pykeg.core import models
from pykeg.web.kegweb import forms
from pykeg.web.api import apikey
from pykeg.connections.foursquare import forms as foursquare_forms
from pykeg.connections.twitter import forms as twitter_forms

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
def connections(request):
  user = request.user
  context = RequestContext(request)

  twitter_profile = None
  try:
    twitter_profile = sr_twitter_models.TwitterProfile.objects.get(user=user)
  except sr_twitter_models.TwitterProfile.DoesNotExist:
    pass
  context['twitter_profile'] = twitter_profile
  context['twitter_settings_form'] = twitter_forms.TwitterSettingsForm()
  if twitter_profile:
    context['twitter_settings_form'] = twitter_forms.TwitterSettingsForm(instance=twitter_profile.settings)

  foursquare_profile = None
  try:
    foursquare_profile = sr_foursquare_models.FoursquareProfile.objects.get(user=user)
  except sr_foursquare_models.FoursquareProfile.DoesNotExist:
    pass
  context['foursquare_profile'] = foursquare_profile
  context['foursquare_settings_form'] = foursquare_forms.FoursquareSettingsForm()
  if foursquare_profile:
    context['foursquare_settings_form'] = foursquare_forms.FoursquareSettingsForm(instance=foursquare_profile.settings)

  return render_to_response('account/connections.html', context)

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
@require_POST
def regenerate_api_key(request):
  form = forms.RegenerateApiKeyForm(request.POST)
  if form.is_valid():
    profile = request.user.get_profile()
    profile.api_secret = apikey.ApiKey.NewSecret()
    profile.save()
  return redirect_to(request, url='/account')

@login_required
@require_POST
def remove_twitter(request):
  form = twitter_forms.UnlinkTwitterForm(request.POST)
  if form.is_valid():
    sr_twitter_models.TwitterProfile.objects.filter(user=request.user).delete()
  # TODO(mikey): HttpResponseRedirect
  return redirect_to(request, url='/account')

@login_required
@require_POST
def update_twitter_settings(request):
  user = request.user
  twitter_profile = sr_twitter_models.TwitterProfile.objects.get(user=user)
  form = twitter_forms.TwitterSettingsForm(request.POST, instance=twitter_profile.settings)
  if form.is_valid():
    form.save()
    messages.success(request, 'Twitter settings were successfully updated.')
  # TODO(mikey): HttpResponseRedirect
  return redirect_to(request, url='/account')

@login_required
@require_POST
def remove_foursquare(request):
  form = foursquare_forms.UnlinkFoursquareForm(request.POST)
  if form.is_valid():
    sr_foursquare_models.FoursquareProfile.objects.filter(user=request.user).delete()
  # TODO(mikey): HttpResponseRedirect
  return redirect_to(request, url='/account')

@login_required
@require_POST
def update_foursquare_settings(request):
  user = request.user
  foursquare_profile = sr_foursquare_models.FoursquareProfile.objects.get(user=user)
  form = foursquare_forms.FoursquareSettingsForm(request.POST, instance=foursquare_profile.settings)
  if form.is_valid():
    form.save()
    messages.success(request, 'Foursquare settings were successfully updated.')
  # TODO(mikey): HttpResponseRedirect
  return redirect_to(request, url='/account')
