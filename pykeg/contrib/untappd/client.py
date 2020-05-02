from builtins import object
import requests
from requests_oauthlib import OAuth2Session


class UntappdClient(object):
    AUTHORIZATION_URL = "https://untappd.com/oauth/authenticate/"
    ACCESS_TOKEN_URL = "https://untappd.com/oauth/authorize/"

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret

    def get_authorization_url(self, redirect_uri):
        oauth = OAuth2Session(self.client_id, redirect_uri=redirect_uri)
        return oauth.authorization_url(self.AUTHORIZATION_URL)

    def handle_authorization_callback(self, response_url, redirect_uri):
        oauth = OAuth2Session(self.client_id, redirect_uri=redirect_uri)
        token = oauth.fetch_token(
            self.ACCESS_TOKEN_URL,
            authorization_response=response_url,
            client_secret=self.client_secret,
            method="GET",
        )
        return token

    def get_user_info(self, access_token):
        return requests.get(
            "https://api.untappd.com/v4/user/info", params={"access_token": access_token}
        ).json()["response"]["user"]
