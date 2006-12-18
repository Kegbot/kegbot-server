from django.conf.urls.defaults import *

urlpatterns = patterns('pykegweb.kegweb.views',
      # main page
      (r'^$', 'index'),

      # keg related
      (r'^kegs/$', 'keg_list'),
      (r'^kegs/(?P<keg_id>\d+)', 'keg_detail'),
      # redirects to the above for compatibility
      (r'^keg/(?P<keg_id>\d+)', 'redirect_to', {'url': '/kegs/%(keg_id)s'}),

      # drinkers
      (r'^drinkers/$', 'user_list'),
      (r'^drinkers/(?P<user_id>\d+)', 'user_detail'),
      (r'^drinkers/(?P<username>\w+)', 'user_detail'),
      # redirects to the above for compatibility
      (r'^drinker/(?P<user_id>\d+)', 'redirect_to', {'url': '/drinkers/%(user_id)s'}),
      (r'^drinker/(?P<username>\w+)', 'redirect_to', {'url': '/drinkers/%(username)s'}),

      # drink related
      (r'^drinks/$', 'drink_list'),
      (r'^drinks/(?P<drink_id>\d+)', 'drink_detail'),
      # redirects to the above for compatibility
      (r'^drink/(?P<drink_id>\d+)', 'redirect_to', {'url': '/drinks/%(drink_id)s'}),

      # still TODO:
      # account management
      # leader boards
      # graphing
)
