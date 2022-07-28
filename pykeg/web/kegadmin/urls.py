from django.urls import path

from pykeg.plugin import util
from pykeg.web.kegadmin import views

urlpatterns = [
    # main page
    path(r"", views.dashboard, name="kegadmin-dashboard"),
    path("settings/general/", views.general_settings, name="kegadmin-main"),
    path("settings/location/", views.location_settings, name="kegadmin-location-settings"),
    path("settings/advanced/", views.advanced_settings, name="kegadmin-advanced-settings"),
    path("bugreport/", views.bugreport, name="kegadmin-bugreport"),
    path("export/", views.export, name="kegadmin-export"),
    path("beers/", views.beverages_list, name="kegadmin-beverages"),
    path("beers/add/", views.beverage_add, name="kegadmin-add-beverage"),
    path("beers/<int:beer_id>/", views.beverage_detail, name="kegadmin-edit-beverage"),
    path("devices/link/", views.link_device, name="kegadmin-link-device"),
    path("kegs/", views.keg_list, name="kegadmin-kegs"),
    path("kegs/online/", views.keg_list_online, name="kegadmin-kegs-online"),
    path("kegs/available/", views.keg_list_available, name="kegadmin-kegs-available"),
    path("kegs/kicked/", views.keg_list_kicked, name="kegadmin-kegs-kicked"),
    path("kegs/add/", views.keg_add, name="kegadmin-add-keg"),
    path("kegs/<int:keg_id>/", views.keg_detail, name="kegadmin-edit-keg"),
    path("brewers/", views.beverage_producer_list, name="kegadmin-beverage-producers"),
    path("brewers/add/", views.beverage_producer_add, name="kegadmin-add-beverage-producer"),
    path(
        "brewers/<int:brewer_id>/",
        views.beverage_producer_detail,
        name="kegadmin-edit-beverage-producer",
    ),
    path("controllers/", views.controller_list, name="kegadmin-controllers"),
    path("controllers/create/", views.add_controller, name="kegadmin-add-controller"),
    path(
        "controllers/<int:controller_id>/",
        views.controller_detail,
        name="kegadmin-edit-controller",
    ),
    path("taps/", views.tap_list, name="kegadmin-taps"),
    path("taps/create/", views.add_tap, name="kegadmin-add-tap"),
    path("taps/<int:tap_id>/", views.tap_detail, name="kegadmin-edit-tap"),
    path("users/", views.user_list, name="kegadmin-users"),
    path("users/<int:user_id>/", views.user_detail, name="kegadmin-edit-user"),
    path("drinks/", views.drink_list, name="kegadmin-drinks"),
    path("drinks/<int:drink_id>/", views.drink_edit, name="kegadmin-edit-drink"),
    path("tokens/", views.token_list, name="kegadmin-tokens"),
    path("tokens/create/", views.add_token, name="kegadmin-add-token"),
    path("tokens/<int:token_id>/", views.token_detail, name="kegadmin-edit-token"),
    path(
        "autocomplete/beverage/",
        views.autocomplete_beverage,
        name="kegadmin-autocomplete-beverage",
    ),
    path("autocomplete/user/", views.autocomplete_user, name="kegadmin-autocomplete-user"),
    path("autocomplete/token/", views.autocomplete_token, name="kegadmin-autocomplete-token"),
    path("plugin/<str:plugin_name>/", views.plugin_settings, name="kegadmin-plugin-settings"),
    path("email/", views.email, name="kegadmin-email"),
    path("logs/", views.logs, name="kegadmin-logs"),
    path("users/create/", views.add_user, name="kegadmin-add-user"),
]

if util.get_plugins():
    urlpatterns += util.get_admin_urls()
