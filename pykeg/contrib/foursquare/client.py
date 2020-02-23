# Copyright 2017 Bevbot LLC, All Rights Reserved
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

from builtins import object
import foursquare


class FoursquareClient(object):
    AUTHORIZATION_URL = 'https://foursquare.com/oauth2/authorize'
    ACCESS_TOKEN_URL = 'https://foursquare.com/oauth2/token'

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret

    def get_authorization_url(self, redirect_uri):
        fs = foursquare.Foursquare(client_id=self.client_id, client_secret=self.client_secret,
            redirect_uri=redirect_uri)
        return fs.oauth.auth_url()

    def handle_authorization_callback(self, code, redirect_uri):
        fs = foursquare.Foursquare(client_id=self.client_id, client_secret=self.client_secret,
            redirect_uri=redirect_uri)
        return fs.oauth.get_token(code)

    def venues(self, venue_id):
        fs = foursquare.Foursquare(client_id=self.client_id, client_secret=self.client_secret)
        return fs.venues(venue_id)

    def users(self, access_token):
        fs = foursquare.Foursquare(access_token=access_token)
        return fs.users()
