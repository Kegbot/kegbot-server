from django.conf.urls import url

from pykeg.web.setup_wizard import views

urlpatterns = [
    url(r"^$", views.start, name="setup_wizard_start"),
    url(r"^upgrade/$", views.upgrade, name="setup_upgrade"),
    url(r"^mode/$", views.mode, name="setup_mode"),
    url(r"^setup-accounts/$", views.setup_accounts, name="setup_accounts"),
    url(r"^settings/$", views.site_settings, name="setup_site_settings"),
    url(r"^admin-user/$", views.admin, name="setup_admin"),
    url(r"^finished/$", views.finish, name="setup_finish"),
]
