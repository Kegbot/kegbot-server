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

import requests
from requests_oauthlib import OAuth2Session


class UntappdClient:
    AUTHORIZATION_URL = 'https://untappd.com/oauth/authenticate/'
    ACCESS_TOKEN_URL = 'https://untappd.com/oauth/authorize/'

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret

    def get_authorization_url(self, redirect_uri):
        oauth = OAuth2Session(self.client_id, redirect_uri=redirect_uri)
        return oauth.authorization_url(self.AUTHORIZATION_URL)

    def handle_authorization_callback(self, response_url, redirect_uri):
        oauth = OAuth2Session(self.client_id, redirect_uri=redirect_uri)
        token = oauth.fetch_token(self.ACCESS_TOKEN_URL,
            authorization_response=response_url,
            client_secret=self.client_secret,
            method='GET')
        return token

    def get_user_info(self, access_token):
        return requests.get('https://api.untappd.com/v4/user/info',
            params={'access_token': access_token}).json()['response']['user']
