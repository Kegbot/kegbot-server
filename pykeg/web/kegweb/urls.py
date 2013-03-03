from django.conf.urls.defaults import *

urlpatterns = patterns('pykeg.web.kegweb.views',
      ### main page
      url(r'^$', 'index', name='kb-home'),

      ### accountpage
      url(r'^claim_token/$', 'claim_token', name='kb-claim-token'),

      ### all-time stats
      url(r'^stats/$', 'system_stats', name='kb-stats'),

      ### keg related
      url(r'^kegs/$', 'keg_list', name='kb-kegs'),
      url(r'^kegs/(?P<keg_id>\d+)', 'keg_detail', name='kb-keg'),

      ### drinkers
      url(r'^drinkers/$', 'user_list', name='kb-drinkers'),
      url(r'^drinkers/(?P<username>[\w@.+-_]+)/$', 'user_detail', name='kb-drinker'),

      ### drink related
      url(r'^drinks/(?P<drink_id>\d+)', 'drink_detail', name='kb-drink'),
      url(r'^drink/(?P<drink_id>\d+)', 'short_drink_detail'),
      url(r'^d/(?P<drink_id>\d+)', 'short_drink_detail'),

      ### sessions
      url(r'^session/(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})/(?P<seqn>\d+)/(?P<slug>[-\w]+)',
          'session_detail', name='kb-session'),

      url(r'^session/(?P<session_id>\d+)/$', 'short_session_detail'),
      url(r'^s/(?P<session_id>\d+)/$', 'short_session_detail'),

)

