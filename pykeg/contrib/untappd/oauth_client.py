from django.conf import settings
from socialregistration.clients.oauth import OAuth2
from socialregistration.settings import SESSION_KEY
import json
import urllib


class Untappd(OAuth2):
    client_id = getattr(settings, 'UNTAPPD_CLIENT_ID', '')
    secret = getattr(settings, 'UNTAPPD_CLIENT_SECRET', '')
    auth_url = 'https://untappd.com/oauth/authenticate'
    access_token_url = 'https://untappd.com/oauth/authorize/'

    def __init__(self, *args, **kwargs):
        self._user_info = None
        self.callback_url = kwargs.pop('callback_url')
        super(Untappd, self).__init__(*args, **kwargs)

    def get_callback_url(self, **kwargs):
        return self.callback_url

    def get_redirect_url(self, state='', **kwargs):
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_url': self.get_callback_url(**kwargs),
            'state': state,
        }

        return '%s?%s' % (self.auth_url, urllib.urlencode(params))

    def parse_access_token(self, content):
        """
        Untappd returns JSON instead of url encoded data.
        """
        response = json.loads(content)
        if not response or not response.get('response'):
            raise ValueError('Malformed response: %s' % str(response))

        return response.get('response', {})

    def request_access_token(self, params):
        params['redirect_url'] = params['redirect_uri']
        del params['redirect_uri']
        params['response_type'] = 'code'
        url = '%s?%s' % (self.access_token_url, urllib.urlencode(params))
        return self.request(url, method="GET")

    def get_user_info(self):
        if self._user_info is None:
            resp, content = self.request('https://api.untappd.com/v4/user/info')
            self._user_info = json.loads(content)['response']['user']
        return self._user_info

    @staticmethod
    def get_session_key():
        return '%suntappd' % SESSION_KEY
