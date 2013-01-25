from django.conf import settings
from django.utils.encoding import smart_unicode
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from socialregistration.clients.oauth import OAuth2
from socialregistration.settings import SESSION_KEY
import urllib
import json

class OAuthError(Exception):
    pass

class Untappd(OAuth2):
    client_id = getattr(settings, 'UNTAPPD_CLIENT_ID', '')
    secret = getattr(settings, 'UNTAPPD_CLIENT_SECRET', '')
    scope = None
    
    auth_url = 'http://untappd.com/oauth/authenticate/'
    access_token_url = 'http://untappd.com/oauth/authorize/'
    
    _user_info = None
    
    
    def get_callback_url(self, **kwargs):
        if self.is_https():
            return 'https://%s%s' % (Site.objects.get_current().domain,
                reverse('untappd:callback'))
        return 'http://%s%s' % (Site.objects.get_current().domain,
            reverse('untappd:callback'))
    
    def parse_access_token(self, content):
        """ 
        Untappd returns JSON instead of url encoded data.
        """
        return json.loads(content)['response']
    
    def request_access_token(self, params):
        """ 
        Untappd does not accept POST requests to retrieve an access token,
        so we'll be doing a GET request instead.
        """
        return self.request(self.access_token_url + '?' + params, method="GET", params=None)
    
    def get_access_token(self, code=None, **params):
        """
        Return the memorized access token or go out and fetch one.
        """
        if self._access_token is None:
            if code is None:
                raise ValueError(_('Invalid code.'))

            self.access_token_dict = self._get_access_token(code, **params)
            try:
                self._access_token = self.access_token_dict['access_token']
            except KeyError, e:
                raise OAuthError(str(self.access_token_dict))

        return self._access_token
        
    def get_redirect_url(self, state='', **kwargs):
        """
        Assemble the URL to where we'll be redirecting the user to to request
        permissions.
        """
        params = 'response_type=code&client_id=' + self.client_id + '&client_secret=' + self.secret + \
            '&redirect_url=' + self.get_callback_url(**kwargs)

        return '%s?%s' % (self.auth_url, params)
    
    
    def _get_access_token(self, code, **params):
        """
        Fetch an access token with the provided `code`.
        """
        params = 'code=' + code + \
            '&client_id=' + self.client_id + \
            '&client_secret=' + self.secret + \
            '&response_type=code' + \
            '&redirect_url=' + self.get_callback_url()
    
        resp, content = self.request_access_token(params=params)
    
        content = smart_unicode(content)
        content = self.parse_access_token(content)
    
        if 'error' in content:
            raise OAuthError(_(
                u"Received error while obtaining access token from %s: %s") % (
                    self.access_token_url, content['error']))
        return content
        
    def request(self, url, method="GET", params=None, headers=None, is_signed=False):
        """
        Make a request against ``url``. By default, the request is signed with
        an access token, but can be turned off by passing ``is_signed=False``.
        """
        params = params or ''
        headers = headers or {}
    
        if method.upper() == "GET":
            if params:
                url = '%s?%s' % (url, params)
            if self._access_token:
                url = url + '?access_token=' + self._access_token
            
            return self.client().request(url, method=method, headers=headers)
        return self.client().request(url, method, body=params,
            headers=headers)
    
    def get_user_info(self):
        if self._user_info is None:
            resp, content = self.request('http://api.untappd.com/v4/user/info')
            try:
                self._user_info = json.loads(content)['response']['user']
            except TypeError:
                raise OAuthError(str(json.loads(content)))
        return self._user_info
    
    @staticmethod
    def get_session_key():
        return '%suntappd' % SESSION_KEY
