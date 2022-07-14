from django.urls import path

from pykeg.web.setup_wizard import views

urlpatterns = [
    path("", views.start, name="setup_wizard_start"),
    path("upgrade/", views.upgrade, name="setup_upgrade"),
    path("mode/", views.mode, name="setup_mode"),
    path("setup-accounts/", views.setup_accounts, name="setup_accounts"),
    path("settings/", views.site_settings, name="setup_site_settings"),
    path("admin-user/", views.admin, name="setup_admin"),
    path("finished/", views.finish, name="setup_finish"),
]
