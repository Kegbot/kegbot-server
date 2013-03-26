from django.conf.urls import patterns
from django.conf.urls import url

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
      url(r'^d/(?P<drink_id>\d+)', 'short_drink_detail', name='kb-drink-short'),

      ### sessions
      url(r'^session/(?P<session_id>\d+)/$', 'short_session_detail'),
      url(r'^s/(?P<session_id>\d+)/$', 'short_session_detail'),

      url(r'^sessions/$', views.SessionArchiveIndexView.as_view(), name='kb-sessions'),
      url(r'^sessions/(?P<year>\d{4})/$', views.SessionYearArchiveView.as_view(), name='kb-sessions-year'),
      url(r'^sessions/(?P<year>\d{4})/(?P<month>\d+)/$',
          views.SessionMonthArchiveView.as_view(month_format='%m'),
          name='kb-sessions-month'),
      url(r'^sessions/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$',
          views.SessionDayArchiveView.as_view(month_format='%m'),
          name='kb-sessions-day'),
      url(r'^sessions/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/(?P<pk>\d+)/$',
          views.SessionDateDetailView.as_view(month_format='%m'),
          name='kb-session-detail'),

)

