# Copyright 2017 Kegbot Project contributors
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
import tweepy
from requests_oauthlib import OAuth1Session
from requests_oauthlib.oauth1_session import TokenMissing
from requests_oauthlib.oauth1_session import TokenRequestDenied

import requests


class TwitterClientError(Exception):
    """Base client error."""


class AuthError(TwitterClientError):
    """Wraps an error raised by oauthlib."""
    def __init__(self, message, cause):
        super(AuthError, self).__init__(message)
        self.cause = cause


class RequestError(TwitterClientError):
    """Wraps an error raised by the request library."""
    def __init__(self, message, cause):
        super(RequestError, self).__init__(message)
        self.cause = cause


class TwitterClient(object):
    REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
    AUTHORIZATION_URL = 'https://api.twitter.com/oauth/authorize'
    ACCESS_TOKEN_URL = 'https://api.twitter.com/oauth/access_token'

    SESSION_RESOURCE_OWNER = 'twitter:resource_owner_key'
    SESSION_RESOURCE_OWNER_SECRET = 'twitter:resource_owner_secret'

    def __init__(self, client_key, client_secret):
        self.client_key = client_key
        self.client_secret = client_secret

    def fetch_request_token(self, callback_uri):
        """Step 1 of flow: Get a request token."""
        session = OAuth1Session(self.client_key,
            client_secret=self.client_secret,
            callback_uri=callback_uri)

        try:
            res = session.fetch_request_token(self.REQUEST_TOKEN_URL)
        except requests.exceptions.RequestException as e:
            raise RequestError('Request error fetching token.', e)
        except (TokenRequestDenied, TokenMissing) as e:
            raise AuthError('Token request failed.', e)

        request_token = res.get('oauth_token')
        request_token_secret = res.get('oauth_token_secret')
        return request_token, request_token_secret

    def get_authorization_url(self, request_token, request_token_secret):
        """Step 2 of flow: Get an authorization url."""
        session = OAuth1Session(self.client_key,
            client_secret=self.client_secret,
            resource_owner_key=request_token,
            resource_owner_secret=request_token_secret)
        return session.authorization_url(self.AUTHORIZATION_URL)

    def get_redirect_url(self, callback_uri):
        """Convenience for steps 1 and 2."""
        request_token, request_token_secret = self.fetch_request_token(callback_uri)
        url = self.get_authorization_url(request_token, request_token_secret)
        return url, request_token, request_token_secret

    def handle_authorization_callback(self, request_token, request_token_secret, request=None, uri=None):
        """Step 3 of the flow: Parse the response and fetch token."""
        session = OAuth1Session(self.client_key,
            client_secret=self.client_secret,
            resource_owner_key=request_token,
            resource_owner_secret=request_token_secret)

        if not uri:
            uri = request.build_absolute_uri() + '?' + request.META.get('QUERY_STRING', '')
        session.parse_authorization_response(uri)

        try:
            res = session.fetch_access_token(self.ACCESS_TOKEN_URL)
        except requests.exceptions.RequestException as e:
            raise RequestError('Request error fetching access token.', e)
        except (TokenRequestDenied, TokenMissing) as e:
            raise AuthError('Auth error fetching access token.', e)

        oauth_token = res.get('oauth_token')
        oauth_token_secret = res.get('oauth_token_secret')
        return oauth_token, oauth_token_secret

    def get_user_info(self, access_token, access_token_secret):
        auth = tweepy.OAuthHandler(self.client_key, self.client_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)
        me = api.me()
        return me
