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

from unittest import TestCase

from pykeg.core import testutils
from . import client

import requests
import requests_mock

vcr = testutils.get_vcr('contrib/twitter')

FAKE_API_KEY = 't47jeS6v2e0QrY7ippyTm4ZQA'
FAKE_API_SECRET = 't5dV0zz9tLOsSgwIBTMd8qrvZ3q2d7hypdeFxw518eyGK647aW'
FAKE_REQUEST_TOKEN = 'Y5DvLwAAAAAA1RVNAAABXOA_xQw'
FAKE_REQUEST_TOKEN_SECRET = 'NJGatgZNsOQRhi0WsQrHrpPb9K3JUc6j'
FAKE_AUTH_URL = 'https://api.twitter.com/oauth/authorize?oauth_token=Y5DvLwAAAAAA1RVNAAABXOA_xQw'
FAKE_CALLBACK_URL = 'http://example.com/redirect?oauth_token=Y5DvLwAAAAAA1RVNAAABXOA_xQw&oauth_verifier=BvnrHp6l6p8tfXEO6b73O3vLX2ytIMPa'
FAKE_OAUTH_TOKEN = '725762360296632320-v5oYdhNkQKWEygfwnLi1dl6cW9o7xhx'
FAKE_OAUTH_TOKEN_SECRET = 'kj3gIsUMyps9cyt6FpcA4rDILomjuwRX5Y7GC2YubZLAb'


class TwitterClientTest(TestCase):
    @vcr.use_cassette()
    def test_fetch_request_token_with_invalid_keys(self):
        c = client.TwitterClient('test', 'test_secret')
        with self.assertRaises(client.AuthError):
            c.fetch_request_token('http://example.com')

    @vcr.use_cassette()
    def test_fetch_request_token_with_no_connection(self):
        c = client.TwitterClient('test', 'test_secret')

        with self.assertRaises(client.RequestError):
            with requests_mock.Mocker() as m:
                m.post(client.TwitterClient.REQUEST_TOKEN_URL, exc=requests.exceptions.ConnectTimeout)
                c.fetch_request_token('http://example.com')

    @vcr.use_cassette()
    def test_fetch_request_token_with_valid_keys(self):
        c = client.TwitterClient(FAKE_API_KEY, FAKE_API_SECRET)
        result = c.fetch_request_token('http://example.com/redirect')
        request_token, request_token_secret = result
        self.assertEqual(FAKE_REQUEST_TOKEN, request_token)
        self.assertEqual(FAKE_REQUEST_TOKEN_SECRET, request_token_secret)

    @vcr.use_cassette()
    def test_get_authorization_url_with_valid_keys(self):
        c = client.TwitterClient(FAKE_API_KEY, FAKE_API_SECRET)
        result = c.get_authorization_url(FAKE_REQUEST_TOKEN, FAKE_REQUEST_TOKEN_SECRET)
        self.assertEqual(FAKE_AUTH_URL, result)

    @vcr.use_cassette()
    def test_handle_authorization_callback(self):
        c = client.TwitterClient(FAKE_API_KEY, FAKE_API_SECRET)
        token, token_secret = c.handle_authorization_callback(
            FAKE_REQUEST_TOKEN, FAKE_REQUEST_TOKEN_SECRET, uri=FAKE_CALLBACK_URL)
        self.assertEqual(FAKE_OAUTH_TOKEN, token)
        self.assertEqual(FAKE_OAUTH_TOKEN_SECRET, token_secret)

    @vcr.use_cassette()
    def test_handle_authorization_callback_with_no_connection(self):
        c = client.TwitterClient(FAKE_API_KEY, FAKE_API_SECRET)

        with self.assertRaises(client.RequestError):
            with requests_mock.Mocker() as m:
                m.post(client.TwitterClient.ACCESS_TOKEN_URL, exc=requests.exceptions.ConnectTimeout)
                c.handle_authorization_callback(
                    FAKE_REQUEST_TOKEN, FAKE_REQUEST_TOKEN_SECRET, uri=FAKE_CALLBACK_URL)
