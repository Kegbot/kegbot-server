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

import cStringIO
import datetime

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic.simple import redirect_to

from pykeg.core import backup
from pykeg.core import models

from pykeg.web.kegadmin import forms

@staff_member_required
def kegadmin_main(request):
  context = RequestContext(request)
  form = forms.SiteSettingsForm(instance=request.kbsite.settings)
  if request.method == 'POST':
    form = forms.SiteSettingsForm(request.POST, instance=request.kbsite.settings)
    if form.is_valid():
      form.save()
  context['settings_form'] = form
  return render_to_response('kegadmin/index.html', context)

@staff_member_required
def tap_list(request):
  context = RequestContext(request)
  taps = request.kbsite.taps.all()
  all_taps = []
  for tap in taps:
    tinfo = {'tap' : tap}
    if tap.current_keg:
      tinfo['end_form'] = forms.KegHiddenSelectForm(initial={'keg':tap.current_keg})
    all_taps.append(tinfo)
  context['all_taps'] = all_taps
  context['create_tap_form'] = forms.CreateTapForm()
  return render_to_response('kegadmin/tap-edit.html', context)

@staff_member_required
def do_end_keg(request):
  if request.method == 'POST':
    form = forms.KegHiddenSelectForm(request.POST)
    if form.is_valid():
      keg = form.cleaned_data['keg']
      if keg.site == request.kbsite:
        keg.status = "offline"
        keg.enddate = datetime.datetime.now()
        keg.save()
        if keg.current_tap:
          keg.current_tap.current_keg = None
          keg.current_tap.save()
        messages.success(request, 'The keg was deactivated.')
  result_url = reverse('kegadmin-taps', args=[request.kbsite.url()])
  return redirect_to(request, result_url)

@staff_member_required
def edit_tap(request, tap_id):
  context = RequestContext(request)
  tap = get_object_or_404(models.KegTap, site=request.kbsite, seqn=tap_id)

  form = forms.ChangeKegForm()
  if request.method == 'POST':
    form = forms.ChangeKegForm(request.POST)
    if form.is_valid():
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

  context['taps'] = request.kbsite.taps.all()
  context['change_keg_form'] = form
  context['create_tap_form'] = forms.CreateTapForm()
  return render_to_response('kegadmin/tap-edit.html', context)

@staff_member_required
def create_tap(request):
  context = RequestContext(request)
  form = forms.ChangeKegForm()

@staff_member_required
def edit_keg(request, keg_id):
  context = RequestContext(request)

@staff_member_required
def backup_restore(request):
  context = RequestContext(request)
  return render_to_response('kegadmin/backup-restore.html', context)

@staff_member_required
def generate_backup(request):
  context = RequestContext(request)

  indent = None
  indent_param = request.GET.get('indent', None)
  if indent_param:
    try:
      indent = int(indent_param)
    except ValueError:
      pass

  kbsite = request.kbsite
  datestr = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
  filename = 'kegbot-%s.%s.json.txt' % (kbsite.name, datestr)

  output_fp = cStringIO.StringIO()
  backup.dump(output_fp, kbsite, indent=indent)

  response = HttpResponse(output_fp.getvalue(),
      mimetype="application/octet-stream")
  response['Content-Disposition'] = 'attachment; filename=%s' % filename
  output_fp.close()
  return response
