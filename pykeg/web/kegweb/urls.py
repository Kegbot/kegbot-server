from django.conf.urls import url

from . import views

urlpatterns = [
    # main page
    url(r'^$', views.index, name='kb-home'),

    # stats
    url(r'^stats/$', views.system_stats, name='kb-stats'),

    # kegs
    url(r'^kegs/$', views.KegListView.as_view(), name='kb-kegs'),
    url(r'^kegs/(?P<keg_id>\d+)/?$', views.keg_detail, name='kb-keg'),
    url(r'^kegs/(?P<keg_id>\d+)/sessions/?$', views.keg_sessions, name='kb-keg-sessions'),

    # fullscreen mode
    url(r'^fullscreen/?$', views.fullscreen, name='kb-fullscreen'),

    # drinkers
    url(r'^drinkers/(?P<username>[\w@\.+\-_]+)/?$', views.user_detail, name='kb-drinker'),
    url(r'^drinkers/(?P<username>[\w@\.+\-_]+)/sessions/?$', views.drinker_sessions,
        name='kb-drinker-sessions'),

    # drinks
    url(r'^drinks/(?P<drink_id>\d+)/?$', views.drink_detail, name='kb-drink'),
    url(r'^drink/(?P<drink_id>\d+)/?$', views.short_drink_detail),
    url(r'^d/(?P<drink_id>\d+)/?$', views.short_drink_detail, name='kb-drink-short'),

    # sessions
    url(r'^session/(?P<session_id>\d+)/?$', views.short_session_detail),
    url(r'^s/(?P<session_id>\d+)/?$', views.short_session_detail, name='kb-session-short'),

    url(r'^sessions/$', views.SessionArchiveIndexView.as_view(), name='kb-sessions'),
    url(r'^sessions/(?P<year>\d{4})/$',
        views.SessionYearArchiveView.as_view(),
        name='kb-sessions-year'),
    url(r'^sessions/(?P<year>\d{4})/(?P<month>\d+)/$',
        views.SessionMonthArchiveView.as_view(month_format='%m'),
        name='kb-sessions-month'),
    url(r'^sessions/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$',
        views.SessionDayArchiveView.as_view(month_format='%m'),
        name='kb-sessions-day'),
    url(r'^sessions/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/(?P<pk>\d+)/?$',
        views.SessionDateDetailView.as_view(month_format='%m'),
        name='kb-session-detail'),
]
