from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic.simple import redirect_to

@login_required
def account_settings(request):
  context = RequestContext(request)
  profile = request.user.get_profile().TwitterProfile()
  if not profile:
    return render_to_response('contrib/twitter/link.html', context)
  return render_to_response('contrib/twitter/settings.html', context)
