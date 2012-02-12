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
from django.forms import widgets
from django.views.decorators.http import require_POST

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
      messages.success(request, 'Site settings were successfully updated.')
  context['settings_form'] = form
  return render_to_response('kegadmin/index.html', context)

@staff_member_required
def tap_list(request):
  context = RequestContext(request)
  taps = [{'tap': tap} for tap in request.kbsite.taps.all()]
  for tinfo in taps:
    tap = tinfo['tap']
    prefix = 'tap-%s' % tap.seqn
    tinfo['prefix'] = prefix

    # Demux multiple forms using submit button name.
    submit_name = "%s-submit" % prefix
    edit_form = None
    if request.method == 'POST' and submit_name in request.POST:
      edit_form = forms.TapForm(request.POST, site=request.kbsite, instance=tap, prefix=prefix)
      if edit_form.is_valid():
        tap = edit_form.save(commit=False)
        val = edit_form.cleaned_data['ml_per_tick']
        ml = val[0]
        if ml == '0':
          ml = val[1]
        tap.ml_per_tick = float(ml)
        tap.save()
        messages.success(request, 'Tap "%s" was updated.' % tap.name)
      else:
        messages.error(request, 'Your form had errors, please correct them.')
    if not edit_form:
      edit_form = forms.TapForm(site=request.kbsite, instance=tap,
          prefix=prefix, initial={'ml_per_tick': (str(tap.ml_per_tick), str(tap.ml_per_tick))})

    for field in edit_form.fields.values():
      widget = field.widget
      if widget.is_hidden:
        continue
      if isinstance(widget, widgets.Textarea) or isinstance(widget, widgets.TextInput):
        new_class = widget.attrs.get('class', '') + ' span10'
        #widget.attrs['class'] = new_class.strip()

    tinfo['edit_form'] = edit_form
    if tap.current_keg and tap.current_keg.is_active():
      tinfo['end_form'] = forms.KegHiddenSelectForm(initial={'keg':tap.current_keg})
    else:
      tinfo['keg_form'] = forms.ChangeKegForm()

  context['all_taps'] = taps
  context['create_tap_form'] = forms.TapForm(site=request.kbsite)
  return render_to_response('kegadmin/tap-edit.html', context)

@staff_member_required
@require_POST
def do_end_keg(request):
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
@require_POST
def edit_tap(request, tap_id):
  context = RequestContext(request)
  tap = get_object_or_404(models.KegTap, site=request.kbsite, seqn=tap_id)
  form = forms.ChangeKegForm()

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
    messages.success(request, 'The new keg was activated. Bottoms up!')
    form = forms.ChangeKegForm()

  result_url = reverse('kegadmin-taps', args=[request.kbsite.url()])
  return redirect_to(request, result_url)

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

  fmt = request.GET.get('fmt', 'minjson')
  if fmt == 'json':
    indent = 2
  else:
    indent = None
    fmt = 'minjson'

  kbsite = request.kbsite
  datestr = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
  filename = 'kegbot-%s.%s.%s.txt' % (kbsite.name, datestr, fmt)

  output_fp = cStringIO.StringIO()
  backup.dump(output_fp, kbsite, indent=indent)

  response = HttpResponse(output_fp.getvalue(),
      mimetype="application/octet-stream")
  response['Content-Disposition'] = 'attachment; filename=%s' % filename
  output_fp.close()
  return response
