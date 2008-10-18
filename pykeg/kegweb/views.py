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
from django.views.generic.list_detail import object_detail
from django.views.generic.list_detail import object_list
from django.views.generic.simple import direct_to_template
from django.views.generic.simple import redirect_to

from pykeg.core import models
from pykeg.core import units
from pykeg.kegweb import view_util
from pykeg.kegweb import charts

# TODO: figure out how to get the appname (places that reference 'kegweb') and
# use that instead

### common stuff

def default_context(request):
  c = {}
  c['top_5'] = view_util.keg_drinkers_by_volume(view_util.current_keg())
  c['boxsize'] = 100
  if request.user.is_authenticated():
    c['logged_in_user'] = request.user
  else:
    c['logged_in_user'] = None
  return c

### views

def index(request):
  context = default_context(request)
  context['last_drinks'] = models.Drink.objects.filter(status='valid').order_by('-id')[:5]
  context['template'] = 'index.html'
  return render_to_response('index.html', context)

def leaders(request):
  context = default_context(request)
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

  drinks = models.Drink.objects.filter(user__exact=user_list[0], volume__gt=0).order_by('-starttime')
  extra['binges'] = models.Binge.objects.filter(user__exact=user_list[0])
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

  # fetch any binges happening at the same time ("drinking with" feature)
  # TODO: coalesce multiple binges/user
  look_behind = drink.starttime - datetime.timedelta(seconds=60*30)
  look_ahead = drink.starttime + datetime.timedelta(seconds=60*30)
  concurrent_binges = models.Binge.objects.filter(starttime__lte=drink.starttime,
        endtime__gte=drink.starttime)
  concurrent_binges = concurrent_binges.exclude(
        user__exact=drink.user)
  extra['concurrent_binges'] = concurrent_binges

  # fetch the current binge, if it exists
  binges = models.Binge.objects.filter(starttime__lte=drink.endtime,
        endtime__gte=drink.starttime, user__exact=drink.user)
  if binges:
    extra['binge'] = binges[0]

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

  # TODO unbilled activity

  return render_to_response('kegweb/account.html', context)
