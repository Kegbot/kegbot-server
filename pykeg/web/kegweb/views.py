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
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.template import RequestContext
from django.views.decorators.cache import cache_page
from django.views.generic.dates import ArchiveIndexView
from django.views.generic.dates import DateDetailView
from django.views.generic.dates import DayArchiveView
from django.views.generic.dates import MonthArchiveView
from django.views.generic.dates import YearArchiveView
from django.views.generic.list import ListView

from kegbot.util import kbjson

from pykeg.core import models
from pykeg.proto import protolib

from pykeg.web.kegweb import forms
from pykeg.web.kegweb import signals

### main views

@cache_page(30)
def index(request):
  context = RequestContext(request)

  context['taps'] = models.KegTap.objects.all()

  events = models.SystemEvent.objects.all()[:10]
  context['initial_events'] = kbjson.dumps([protolib.ToDict(e, full=True) for e in events],
      indent=None)

  sessions = models.DrinkingSession.objects.all().order_by('-id')[:10]
  context['sessions'] = sessions
  context['initial_sessions'] = kbjson.dumps([protolib.ToDict(s, full=True) for s in sessions],
      indent=None)

  taps = models.KegTap.objects.filter(current_keg__isnull=False)
  context['initial_taps'] = kbjson.dumps([protolib.ToDict(t, full=True) for t in taps], indent=None)

  context['have_events'] = len(events) > 0
  context['have_taps'] = len(taps) > 0

  return render_to_response('index.html', context_instance=context)

@cache_page(30)
def system_stats(request):
  stats = models.KegbotSite.get().GetStats()
  context = RequestContext(request, {
    'stats': stats,
  })

  top_drinkers = []
  for username, vol in stats.get('volume_by_drinker', {}).iteritems():
    try:
      user = models.User.objects.get(username=username)
    except models.User.DoesNotExist:
      continue  # should not happen
    top_drinkers.append((vol, user))
  top_drinkers.sort(reverse=True)

  context['top_drinkers'] = top_drinkers[:10]

  return render_to_response('kegweb/system-stats.html', context_instance=context)


### object lists and detail (generic views)

def user_detail(request, username):
  user = get_object_or_404(models.User, username=username, is_active=True)
  stats = user.get_profile().GetStats()

  # TODO(mikey): Limit to "recent" sessions for now.
  # Bug: https://github.com/Kegbot/kegbot/issues/37
  chunks = models.UserSessionChunk.objects.filter(user=user).select_related(depth=1)[:10]
  drinks = user.drinks.all()

  context = RequestContext(request, {
      'drinks': drinks,
      'chunks': chunks,
      'stats': stats,
      'drinker': user})
  return render_to_response('kegweb/drinker_detail.html', context_instance=context)

class KegListView(ListView):
  model = models.Keg
  template_name = 'kegweb/keg_list.html'
  context_object_name = 'kegs'
  paginate_by = 10

  def get_queryset(self):
    return models.Keg.objects.all().order_by('-id')

@cache_page(30)
def keg_detail(request, keg_id):
  keg = get_object_or_404(models.Keg, id=keg_id)
  sessions = keg.Sessions()
  context = RequestContext(request, {
    'keg': keg,
    'stats': keg.GetStats(),
    'sessions': sessions})
  return render_to_response('kegweb/keg_detail.html', context_instance=context)

def short_drink_detail(request, drink_id):
  return redirect('kb-drink', drink_id=str(drink_id), permanent=True)

def short_session_detail(request, session_id):
  session = get_object_or_404(models.DrinkingSession, id=session_id)
  url = session.get_absolute_url()
  return redirect(url, permanent=True)

def drink_detail(request, drink_id):
  drink = get_object_or_404(models.Drink, id=drink_id)
  context = RequestContext(request, {'drink': drink})
  return render_to_response('kegweb/drink_detail.html', context_instance=context)

def session_detail(request, year, month, day, id, slug):
  session = get_object_or_404(models.DrinkingSession, id=id)
  context = RequestContext(request, {
    'session': session,
    'stats': session.GetStats(),
  })
  return render_to_response('kegweb/session_detail.html', context_instance=context)


class SessionArchiveIndexView(ArchiveIndexView):
  model = models.DrinkingSession
  date_field = 'start_time'
  template_name = 'kegweb/drinkingsession_archive.html'
  context_object_name = 'sessions'
  paginate_by = 20


class SessionYearArchiveView(YearArchiveView):
  model = models.DrinkingSession
  date_field = 'start_time'
  template_name = 'kegweb/drinkingsession_archive_year.html'
  make_object_list = True
  context_object_name = 'sessions'
  paginate_by = 20


class SessionMonthArchiveView(MonthArchiveView):
  model = models.DrinkingSession
  date_field = 'start_time'
  template_name = 'kegweb/drinkingsession_archive_month.html'
  make_object_list = True
  context_object_name = 'sessions'
  paginate_by = 20


class SessionDayArchiveView(DayArchiveView):
  model = models.DrinkingSession
  date_field = 'start_time'
  template_name = 'kegweb/drinkingsession_archive_day.html'
  make_object_list = True
  context_object_name = 'sessions'
  paginate_by = 20


class SessionDateDetailView(DateDetailView):
  model = models.DrinkingSession
  date_field = 'start_time'
  template_name = 'kegweb/session_detail.html'
  context_object_name = 'session'

  def get_context_data(self, **kwargs):
    """Adds `stats` to the context."""
    ret = super(SessionDateDetailView, self).get_context_data(**kwargs)
    ret['stats'] = ret[self.context_object_name].GetStats()
    return ret

