from django.conf.urls.defaults import *

urlpatterns = patterns('pykeg.web.kegweb.views',
      ### main page
      url(r'^$', 'index', name='kb-home'),

      ### accountpage
      url(r'^claim_token/$', 'claim_token', name='kb-claim-token'),

      ### all-time stats
      url(r'^stats/$', 'system_stats', name='kb-stats'),
      url(r'^leaders/$', 'redirect_to', {'url': '/stats/'}),

      ### keg related
      url(r'^kegs/$', 'keg_list', name='kb-kegs'),
      url(r'^kegs/(?P<keg_id>\d+)', 'keg_detail', name='kb-keg'),
      # redirects to the above for compatibility
      (r'^keg/(?P<keg_id>\d+)', 'redirect_to', {'url': '/kegs/%(keg_id)s'}),

      ### drinkers
      url(r'^drinkers/$', 'user_list', name='kb-drinkers'),
      url(r'^drinkers/(?P<username>[\w@.+-_]+)/$', 'user_detail', name='kb-drinker'),
      url(r'^drinkers/(?P<user_id>\d+)/$', 'user_detail_by_id'),
      # redirects to the above for compatibility
      (r'^drinker/(?P<user_id>\d+)/$', 'redirect_to', {'url': '/drinkers/%(user_id)s'}),
      (r'^drinker/(?P<username>[\w@.+-_]+)/$', 'redirect_to', {'url': '/drinkers/%(username)s'}),

      ### drink related
      url(r'^drinks/(?P<drink_id>\d+)', 'drink_detail', name='kb-drink'),
      # redirects to the above for compatibility
      (r'^drink/(?P<drink_id>\d+)', 'redirect_to', {'url': '/drinks/%(drink_id)s'}),
      (r'^d/(?P<drink_id>\d+)', 'redirect_to', {'url': '/drinks/%(drink_id)s'}),

      ### sessions
      url(r'^session/(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})/(?P<seqn>\d+)/(?P<slug>[-\w]+)',
          'session_detail', name='kb-session')

)

