from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic.simple import redirect_to

from pykeg.contrib.facebook import fbutil
from pykeg.contrib.facebook import models
from pykeg.web.contrib.facebook import forms

import facebook

@login_required
def update_perms(request):
  context = RequestContext(request)
  models.FacebookSession.get_session(request)
  # TODO(mikey): record permissions in table.
  raise Http404

@login_required
def account_settings(request):
  profile = fbutil.profile_for_user(request.user)
  if not profile:
    raise Http404

  settings = profile.settings.all()[0]
  form = forms.FacebookSettingsForm(instance=settings)
  if request.method == 'POST':
    form = forms.FacebookSettingsForm(request.POST, instance=settings)
    if form.is_valid():
      profile = fbutil.profile_for_user(request.user)
      if not profile:
        raise ValueError, "Bad profile"
      settings = form.save(commit=False)
      settings.profile = profile
      settings.save()
  else:
    form = forms.FacebookSettingsForm()
  context = RequestContext(request)
  context['settings_form'] = form
  return render_to_response('contrib/facebook/settings.html', context)

@login_required
def status_update(request):
  if request.method == 'POST':
    form = forms.WallPostForm(request.POST)
    if form.is_valid():
      fbutil.stream_publish(request.user, message=form.cleaned_data['message'])
  context = {'form': forms.WallPostForm()}
  return render_to_response('contrib/facebook/status-update.html', context)
