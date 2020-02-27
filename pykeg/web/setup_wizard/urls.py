# Copyright 2014 Kegbot Project contributors
#
# This file is part of the Pykeg package of the Kegbot project.
# For more information on Pykeg or Kegbot, see http://kegbot.org/
#
# Pykeg is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# Pykeg is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pykeg.  If not, see <http://www.gnu.org/licenses/>.

from django.conf.urls import url

from pykeg.web.setup_wizard import views

urlpatterns = [
    url(r'^$', views.start, name='setup_wizard_start'),
    url(r'^setup-accounts/$', views.setup_accounts, name='setup_accounts'),
    url(r'^settings/$', views.site_settings, name='setup_site_settings'),
    url(r'^admin-user/$', views.admin, name='setup_admin'),
    url(r'^finished/$', views.finish, name='setup_finish'),
]
