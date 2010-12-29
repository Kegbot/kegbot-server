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

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.template import RequestContext
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response

from pykeg.core import models

from pykeg.web.kegadmin import forms

@staff_member_required
def kegadmin_main(request):
  context = RequestContext(request)
  return render_to_response('kegadmin/index.html', context)

@staff_member_required
def change_kegs(request):
  context = RequestContext(request)
  form = forms.ChangeKegForm()
  if request.method == 'POST':
    form = forms.ChangeKegForm(request.POST)
    if form.is_valid():
      tap = form.cleaned_data['tap']
      current = tap.current_keg
      if current and current.status != 'offline':
        current.status = 'offline'
        current.save()

      new_keg = models.Keg()
      new_keg.site = request.kbsite
      new_keg.type = form.cleaned_data['beer_type']
      new_keg.size = form.cleaned_data['keg_size']
      new_keg.status = 'online'
      if form.cleaned_data['description']:
        new_keg.description = form.cleaned_data['description']
      new_keg.save()
      tap.current_keg = new_keg
      tap.save()
      messages.success(request, 'The new keg was activated.')
      form = forms.ChangeKegForm()
  context['change_keg_form'] = form
  return render_to_response('kegadmin/change-kegs.html', context)

@staff_member_required
def tap_list(request):
  context = RequestContext(request)
  context['taps'] = request.kbsite.taps.all()
  return render_to_response('kegadmin/tap-list.html', context)

@staff_member_required
def edit_tap(request, tap_id):
  context = RequestContext(request)
  context['taps'] = request.kbsite.taps.all()
  tap = get_object_or_404(models.KegTap, site=request.kbsite, seqn=tap_id)
  context['tap'] = tap
  context['change_keg_form'] = forms.ChangeKegForm()
  return render_to_response('kegadmin/tap-edit.html', context)

@staff_member_required
def view_stats(request):
  context = RequestContext(request)
  keg_stats = models.KegStats.objects.all()
