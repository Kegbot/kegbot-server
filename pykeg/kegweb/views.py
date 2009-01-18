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
from django.views.decorators.cache import cache_page

from django.http import Http404
from django.shortcuts import render_to_response
from django.views.generic.list_detail import object_detail
from django.views.generic.list_detail import object_list
from django.views.generic.simple import direct_to_template
from django.views.generic.simple import redirect_to

from pykeg.core import models
from pykeg.core import units
from pykeg.kegweb import view_util
from pykeg.kegweb import forms
from pykeg.kegweb import charts
from pykeg.kegweb import models as kegweb_models

# TODO: figure out how to get the appname (places that reference 'kegweb') and
# use that instead

### common stuff

def default_context(request):
  c = {}
  c['top_5'] = view_util.keg_drinkers_by_volume(view_util.current_keg())[:5]
  c['boxsize'] = 100
  if request.user.is_authenticated():
    c['logged_in_user'] = request.user
  else:
    c['logged_in_user'] = None
  return c

### views

@cache_page(30)
def index(request):
  context = default_context(request)
  try:
    page = kegweb_models.Page.objects.get(name__exact='MainPage',
                                          status__exact='published')
  except kegweb_models.Page.DoesNotExist:
    page = None
  context['page_node'] = page
  context['last_drinks'] = models.Drink.objects.filter(status='valid').order_by('-id')[:5]
  context['template'] = 'index.html'
  return render_to_response('index.html', context)

@cache_page(30)
def leaders(request):
  context = default_context(request)
  all_drinks = models.Drink.objects.filter(status='valid')
  context['top_vol_alltime'] = view_util.drinkers_by_volume(all_drinks)
  context['top_vol_current_keg'] = view_util.keg_drinkers_by_volume(view_util.current_keg())
  context['top_bac_alltime'] = []
  return render_to_response('kegweb/leaders.html', context)

### object lists and detail (generic views)

def user_list(request):
  user_list = models.User.objects.all()
  return object_list(request, queryset=user_list, template_object_name='drinker',
      template_name='kegweb/drinker_list.html',
      extra_context=default_context(request))

def user_detail(request, username=None, user_id=None):
  extra = default_context(request)
  params = {
    'extra_context': extra,
    'template_object_name': 'drinker',
    'template_name': 'kegweb/drinker_detail.html',
  }

  if username:
    user_list = models.User.objects.filter(username__exact=username)
    params['slug'] = username
    params['slug_field'] = 'username'
  elif user_id:
    user_list = models.User.objects.filter(id__exact=user_id)
    params['object_id'] = user_id
    if user_list:
      return redirect_to(request, url='/drinker/'+user_list[0].username)
  else:
    raise Http404

  user = user_list[0]
  drinks = user.drink_set.filter(volume__gt=0, status__exact='valid').order_by('-starttime')
  extra['drinking_sessions'] = user.userdrinkingsession_set.all().order_by('-starttime')
  extra['drinks'] = drinks

  # TODO: fix or remove; broken in kegbotweb
  extra['rating'] = 'unknown'
  extra['avg_drinks_hour'] = 0.0

  if len(drinks):
    extra['first_drink'] = drinks[drinks.count()-1]
    extra['last_drink'] = drinks[0]

  total_volume = units.Quantity(0)
  for d in drinks:
    total_volume += d.Volume()
  extra['total_volume'] = total_volume

  params['queryset'] = user_list
  params['extra_context'] = extra

  return object_detail(request, **params)

def keg_list(request):
  context = default_context(request)
  context['kegs'] = models.Keg.objects.all().order_by('-id')
  return render_to_response('kegweb/keg_list.html', context)

def keg_detail(request, keg_id):
  q = models.Keg.objects.filter(id__exact=keg_id)
  if not len(q) == 1:
    raise Http404
  keg = q[0]
  extra = default_context(request)

  q2 = models.Keg.objects.filter(id__lt=keg_id).order_by('-id')
  if len(q2):
    extra['prev_keg'] = q2[0]

  q3 = models.Keg.objects.filter(id__gt=keg_id).order_by('id')
  if len(q3):
    extra['next_keg'] = q3[0]

  # load all drinks this keg (for full drink listing block)
  kegdrinks = view_util.keg_drinks(keg).order_by('-id')
  vol_by_user = view_util.drinkers_by_volume(kegdrinks)
  cost_by_user = view_util.drinkers_by_cost(kegdrinks)

  extra['drinks'] = kegdrinks
  extra['ounces_by_user'] = vol_by_user
  extra['cost_by_user'] = cost_by_user
  extra['total_poured'] = keg.served_volume()
  extra['full_volume'] = keg.full_volume()
  extra['pct_full'] = 100.0 * (float(keg.remaining_volume()) / float(keg.full_volume()))

  vol_chart = charts.volume_chart(vol_by_user)
  if vol_chart is not None:
    extra['chart_pie'] = vol_chart.get_url()

  return object_detail(request, queryset=q, object_id=keg_id,
        template_object_name='keg', template_name='kegweb/keg_detail.html',
        extra_context=extra)

def drink_list(request):
  drink_list = models.Drink.objects.filter(volume__gt=0)
  return object_list(request, queryset=drink_list, template_object_name='drink',
        extra_context=default_context(request))

def drink_detail(request, drink_id):
  q = models.Drink.objects.filter(id__exact=drink_id)
  if len(q) != 1:
    raise Http404
  drink = q[0]
  extra = default_context(request)

  drink_session = drink.userdrinkingsessionassignment_set.all()[0].session
  drink_group = drink_session.group

  extra['drink_session'] = drink_session
  extra['drink_group'] = drink_group
  extra['drinking_alone'] = drink_group.GetSessions().count() == 1

  return object_detail(request, queryset=q, object_id=drink_id,
        template_name='kegweb/drink_detail.html', template_object_name='drink',
        extra_context=extra)

@login_required
def account_view(request):
  context = default_context(request)
  user = request.user
  context['statements'] = user.billstatement_set.all().order_by('-statement_date')
  context['payments'] = user.payment_set.all().order_by('-payment_date')
  context['user'] = user
  context['profile_form'] = forms.UserProfileForm(instance=user.get_profile())

  # TODO unbilled activity

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
