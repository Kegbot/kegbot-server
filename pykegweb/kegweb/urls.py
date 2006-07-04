from django.conf.urls.defaults import *
urlpatterns = patterns('pykegweb.kegweb.views',
      # main page
      (r'^$', 'index'),

      # keg related
      (r'^keg/$', 'kegindex'),
      (r'^keg/(?P<keg_id>\d+)', 'kegdetail'),

      # drinkers
      (r'^drinker/(?P<drinker_id>\d+)', 'drinkerdetail'),
)

urlpatterns += patterns('',
      (r'^site_media/(.*)$', 'django.views.static.serve', {'document_root': '/home/mike/svnbox/mjw-trunk/pykegweb/media'}),
)
