from django.conf.urls.defaults import *

from . import views

urlpatterns = patterns('pykeg.web.kegweb.views',
      ### main page
      url(r'^$', 'index', name='kb-home'),

      ### stats
      url(r'^stats/$', 'system_stats', name='kb-stats'),

      ### kegs
      url(r'^kegs/$', views.KegListView.as_view(), name='kb-kegs'),
      url(r'^kegs/(?P<keg_id>\d+)', 'keg_detail', name='kb-keg'),

      ### drinkers
      url(r'^drinkers/(?P<username>[\w@.+-_]+)/$', 'user_detail', name='kb-drinker'),

      ### drinks
      url(r'^drinks/(?P<drink_id>\d+)', 'drink_detail', name='kb-drink'),
      url(r'^drink/(?P<drink_id>\d+)', 'short_drink_detail'),
      url(r'^d/(?P<drink_id>\d+)', 'short_drink_detail'),

      ### sessions
      url(r'^session/(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})/(?P<seqn>\d+)/(?P<slug>[-\w]+)',
          'session_detail', name='kb-session'),
      url(r'^session/(?P<session_id>\d+)/$', 'short_session_detail'),
      url(r'^s/(?P<session_id>\d+)/$', 'short_session_detail'),

)

