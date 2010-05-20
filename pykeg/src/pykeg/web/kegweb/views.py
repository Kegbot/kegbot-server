#!/usr/bin/env python
#
# Copyright 2008 Mike Wakerly <opensource@hoho.com>
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

import datetime

from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.cache import cache_page
from django.views.generic.list_detail import object_detail
from django.views.generic.list_detail import object_list
from django.views.generic.simple import redirect_to

from pykeg.core import models
from pykeg.core import units

from pykeg.web.kegweb import forms
from pykeg.web.kegweb import models as kegweb_models
from pykeg.web.kegweb import view_util

### main views

@cache_page(30)
def index(request):
  context = RequestContext(request)
  try:
    page = kegweb_models.Page.objects.get(name__exact='MainPage',
                                          status__exact='published')
  except kegweb_models.Page.DoesNotExist:
    page = None
  context['page_node'] = page
  context['last_drinks'] = view_util.all_valid_drinks().order_by('-id')[:5]
  context['template'] = 'index.html'
  context['taps'] = models.KegTap.objects.all()
  return render_to_response('index.html', context)

@cache_page(30)
def system_stats(request):
  context = RequestContext(request)
  all_drinks = view_util.all_valid_drinks()
  context['top_volume_drinkers_alltime'] = view_util.drinkers_by_volume(all_drinks)[:10]
  return render_to_response('kegweb/system-stats.html', context)


### object lists and detail (generic views)

def user_list(request):
  user_list = models.User.objects.all()
  return object_list(request,
      queryset=user_list,
      template_object_name='drinker',
      template_name='kegweb/drinker_list.html')

def user_detail(request, username):
  return object_detail(request,
      queryset=models.User.objects.filter(is_active=True),
      slug=username,
      slug_field='username',
      template_name='kegweb/drinker_detail.html',
      template_object_name='drinker')

def user_detail_by_id(request, user_id):
  try:
    user = models.User.objects.get(pk=user_id)
  except models.User.DoesNotExist:
    raise Http404
  return redirect_to(request, url='/drinker/'+user.username)

def keg_list(request):
  all_kegs = models.Keg.objects.all().order_by('-id')
  return object_list(request,
      queryset=all_kegs,
      template_object_name='keg',
      template_name='kegweb/keg_list.html')

@cache_page(30)
def keg_detail(request, keg_id):
  all_kegs = models.Keg.objects.all()
  return object_detail(request,
      queryset=all_kegs,
      object_id=keg_id,
      template_object_name='keg',
      template_name='kegweb/keg_detail.html')

def drink_list(request):
  return object_list(request,
      queryset=view_util.all_valid_drinks(),
      template_name='kegweb/drink_list.html',
      template_object_name='drink')

def drink_detail(request, drink_id):
  return object_detail(request,
      queryset=view_util.all_valid_drinks(),
      object_id=drink_id,
      template_name='kegweb/drink_detail.html',
      template_object_name='drink')

### auth

def webauth(request):
  context = {}
  return render_to_response('kegweb/webauth.html', context)

### account stuff

@login_required
def account_view(request):
  context = RequestContext(request)
  user = request.user
  context['user'] = user
  context['profile_form'] = forms.UserProfileForm(instance=user.get_profile())
  mf = forms.MugshotForm()
  context['mugshot_form'] = mf

  return render_to_response('kegweb/account.html', context)

@login_required
def update_profile(request):
  if request.method != 'POST':
    raise Http404
  orig_profile = request.user.get_profile()
  form = forms.UserProfileForm(request.POST, instance=orig_profile)
  if form.is_valid():
    new_profile = form.save()
  return redirect_to(request, url='/account/')

@login_required
def update_mugshots(request):
  if request.method != 'POST':
    raise Http404

  form = forms.MugshotForm(request.POST, request.FILES)
  if form.is_valid():
    pic = models.UserPicture.objects.create(user=request.user)
    image = request.FILES['new_mugshot']
    pic.image.save(image.name, image)
    pic.save()

    profile = request.user.get_profile()
    profile.mugshot = pic
    profile.save()
  return redirect_to(request, url='/account/')

@login_required
def claim_token(request):
  if request.method == 'POST':
    form = forms.ClaimTokenForm(request.POST)

    if form.is_valid():
      user = form.cleaned_data['user']
      token = form.cleaned_data['token']
      # TODO(mikey): non-superusers should only be able to claim tokens for
      # their own account.
      token.user = user
      token.save()
  else:
    form = forms.ClaimTokenForm()

  context = RequestContext(request)
  context['form'] = form
  return render_to_response('kegweb/claim_token.html', context)

