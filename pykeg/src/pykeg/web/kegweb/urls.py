from django.conf.urls.defaults import *

try:
  from registration.views import register
  from pykeg.web.kegweb.forms import KegbotRegistrationForm
  USE_DJANGO_REGISTRATION = True
except ImportError:
  USE_DJANGO_REGISTRATION = False

urlpatterns = patterns('pykeg.web.kegweb.views',
      ### main page
      (r'^$', 'index'),

      ### accountpage
      (r'^account/$', 'account_view'),
      (r'^account/update_profile/$', 'update_profile'),
      (r'^account/update_mugshots/$', 'update_mugshots'),
      (r'^account/claim_token/$', 'claim_token'),

      ### all-time stats
      (r'^stats/$', 'system_stats'),
      (r'^leaders/$', 'redirect_to', {'url': '/stats/'}),

      ### keg related
      (r'^kegs/$', 'keg_list'),
      url(r'^kegs/(?P<keg_id>\d+)', 'keg_detail', name='keg'),
      # redirects to the above for compatibility
      (r'^keg/(?P<keg_id>\d+)', 'redirect_to', {'url': '/kegs/%(keg_id)s'}),

      ### drinkers
      (r'^drinkers/$', 'user_list'),
      url(r'^drinkers/(?P<username>\w+)', 'user_detail', name='drinker'),
      (r'^drinkers/(?P<user_id>\d+)', 'user_detail_by_id'),
      # redirects to the above for compatibility
      (r'^drinker/(?P<user_id>\d+)', 'redirect_to', {'url': '/drinkers/%(user_id)s'}),
      (r'^drinker/(?P<username>\w+)', 'redirect_to', {'url': '/drinkers/%(username)s'}),

      ### drink related
      (r'^drinks/$', 'drink_list'),
      url(r'^drinks/(?P<drink_id>\d+)', 'drink_detail', name='drink'),
      # redirects to the above for compatibility
      (r'^drink/(?P<drink_id>\d+)', 'redirect_to', {'url': '/drinks/%(drink_id)s'}),
      (r'^d/(?P<drink_id>\d+)', 'redirect_to', {'url': '/drinks/%(drink_id)s'}),

)

### accounts and registration
# uses the stock django-registration views, except we need to override the
# registration class for acocunt/register
if USE_DJANGO_REGISTRATION:
  from django.contrib.auth import views as auth_views
  urlpatterns += patterns('',
    url(r'^accounts/register/$', register,
      {'form_class':KegbotRegistrationForm},
      name='registration_register',
    ),
   (r'^accounts/', include('registration.urls')),
  )

