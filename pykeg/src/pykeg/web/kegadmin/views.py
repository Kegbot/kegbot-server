from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.template import RequestContext
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
        current.save

      new_keg = models.Keg()
      new_keg.type = form.cleaned_data['beer_type']
      new_keg.size = form.cleaned_data['keg_size']
      new_keg.status = 'online'
      if form.cleaned_data['description']:
        new_keg.description = form.cleaned_data['description']
      new_keg.save()
      tap.current_keg = new_keg
      tap.save()
      form = forms.ChangeKegForm()
  context['change_keg_form'] = form
  return render_to_response('kegadmin/change-kegs.html', context)

@staff_member_required
def edit_taps(request):
  context = RequestContext(request)
  tap_forms = [forms.TapForm(x) for x in models.KegTap.objects.all()]
  context['forms'] = tap_forms
  return render_to_response('kegadmin/edit-taps.html', context)
