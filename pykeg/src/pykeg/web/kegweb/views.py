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

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.cache import cache_page
from django.views.generic.list_detail import object_detail
from django.views.generic.list_detail import object_list
from django.views.generic.simple import redirect_to

from pykeg.core import models

from pykeg.web.kegweb import forms
from pykeg.web.kegweb import models as kegweb_models
from pykeg.web.kegweb import signals

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
  context['taps'] = request.kbsite.taps.all()

  try:
    session = request.kbsite.sessions.latest()
    if session.IsActiveNow():
      context['current_session'] = session
  except models.DrinkingSession.DoesNotExist:
    pass

  recent_images = models.Picture.objects.filter(
      site=request.kbsite,
      drink__isnull=False).order_by('-created_date')[:9]
  context['recent_images'] = recent_images

  return render_to_response('index.html', context)

@cache_page(30)
def system_stats(request):
  stats = request.kbsite.GetStats()
  context = RequestContext(request, {
    'stats': stats,
  })

  top_drinkers = []
  for drinkervol in stats.volume_by_drinker:
    username = drinkervol.username
    vol = drinkervol.volume_ml
    try:
      user = models.User.objects.get(username=username)
    except models.User.DoesNotExist:
      continue  # should not happen
    top_drinkers.append((vol, user))
  top_drinkers.sort(reverse=True)

  context['top_drinkers'] = top_drinkers[:10]

  return render_to_response('kegweb/system-stats.html', context)


### object lists and detail (generic views)

def user_list(request):
  user_list = models.User.objects.all()
  return object_list(request,
      queryset=user_list,
      template_object_name='drinker',
      template_name='kegweb/drinker_list.html')

def user_detail(request, username):
  user = get_object_or_404(models.User, username=username)
  try:
    stats = models.UserStats.objects.get(site=request.kbsite, user=user).stats
  except models.UserStats.DoesNotExist:
    stats = None

  # TODO(mikey): Limit to "recent" sessions for now.
  # Bug: https://github.com/Kegbot/kegbot/issues/37
  chunks = models.UserSessionChunk.objects.filter(site=request.kbsite,
      user=user).select_related(depth=1)[:10]
  drinks = user.drinks.filter(site=request.kbsite)

  context = RequestContext(request, {
      'drinks': drinks,
      'chunks': chunks,
      'stats': stats,
      'drinker': user})
  return render_to_response('kegweb/drinker_detail.html', context)

def user_detail_by_id(request, user_id):
  try:
    user = models.User.objects.get(pk=user_id)
  except models.User.DoesNotExist:
    raise Http404
  return redirect_to(request, url='/drinker/'+user.username)

def keg_list(request):
  all_kegs = request.kbsite.kegs.all().order_by('-id')
  return object_list(request,
      queryset=all_kegs,
      template_object_name='keg',
      template_name='kegweb/keg_list.html')

@cache_page(30)
def keg_detail(request, keg_id):
  keg = get_object_or_404(models.Keg, site=request.kbsite, seqn=keg_id)
  sessions = keg.Sessions()
  context = RequestContext(request, {
    'keg': keg,
    'stats': keg.GetStats(),
    'sessions': sessions})
  return render_to_response('kegweb/keg_detail.html', context)

def drink_detail(request, drink_id):
  drink = get_object_or_404(models.Drink, site=request.kbsite, seqn=drink_id)
  context = RequestContext(request, {'drink': drink})
  return render_to_response('kegweb/drink_detail.html', context)

### auth

def webauth(request):
  context = {}
  return render_to_response('kegweb/webauth.html', context)

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

def session_detail(request, year, month, day, seqn, slug):
  session = get_object_or_404(models.DrinkingSession, site=request.kbsite, seqn=seqn)
  context = RequestContext(request, {
    'session': session,
    'stats': session.GetStats(),
  })
  return render_to_response('kegweb/session_detail.html', context)


