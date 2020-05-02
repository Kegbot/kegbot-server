from builtins import object
import foursquare


class FoursquareClient(object):
    AUTHORIZATION_URL = "https://foursquare.com/oauth2/authorize"
    ACCESS_TOKEN_URL = "https://foursquare.com/oauth2/token"

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret

    def get_authorization_url(self, redirect_uri):
        fs = foursquare.Foursquare(
            client_id=self.client_id, client_secret=self.client_secret, redirect_uri=redirect_uri
        )
        return fs.oauth.auth_url()

    def handle_authorization_callback(self, code, redirect_uri):
        fs = foursquare.Foursquare(
            client_id=self.client_id, client_secret=self.client_secret, redirect_uri=redirect_uri
        )
        return fs.oauth.get_token(code)

    def venues(self, venue_id):
        fs = foursquare.Foursquare(client_id=self.client_id, client_secret=self.client_secret)
        return fs.venues(venue_id)

    def users(self, access_token):
        fs = foursquare.Foursquare(access_token=access_token)
        return fs.users()
