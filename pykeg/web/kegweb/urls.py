from django.urls import path

from . import views

urlpatterns = [
    # main page
    path("", views.index, name="kb-home"),
    # stats
    path("stats/", views.system_stats, name="kb-stats"),
    # kegs
    path("kegs/", views.KegListView.as_view(), name="kb-kegs"),
    path("kegs/<int:keg_id>/", views.keg_detail, name="kb-keg"),
    path("kegs/<int:keg_id>/sessions/", views.keg_sessions, name="kb-keg-sessions"),
    # fullscreen mode
    path("fullscreen/", views.fullscreen, name="kb-fullscreen"),
    # drinkers
    path("drinkers/<str:username>/", views.user_detail, name="kb-drinker"),
    path(
        "drinkers/<str:username>/sessions/",
        views.drinker_sessions,
        name="kb-drinker-sessions",
    ),
    # drinks
    path("drinks/<int:drink_id>/", views.drink_detail, name="kb-drink"),
    path("drink/<int:drink_id>/", views.short_drink_detail),
    path("d/<int:drink_id>/", views.short_drink_detail, name="kb-drink-short"),
    # sessions
    path("session/<int:session_id>/", views.short_session_detail),
    path("s/<int:session_id>/", views.short_session_detail, name="kb-session-short"),
    path("sessions/", views.SessionArchiveIndexView.as_view(), name="kb-sessions"),
    path(
        "sessions/<int:year>/",
        views.SessionYearArchiveView.as_view(),
        name="kb-sessions-year",
    ),
    path(
        "sessions/<int:year>/<int:month>/",
        views.SessionMonthArchiveView.as_view(month_format="%m"),
        name="kb-sessions-month",
    ),
    path(
        "sessions/<int:year>/<int:month>/<int:day>/",
        views.SessionDayArchiveView.as_view(month_format="%m"),
        name="kb-sessions-day",
    ),
    path(
        "sessions/<int:year>/<int:month>/<int:day>/<int:pk>/",
        views.SessionDateDetailView.as_view(month_format="%m"),
        name="kb-session-detail",
    ),
]
