import logging
import re

from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed

from pykeg.core import models


class ApiKeyAuthHolder(object):
    """DRF auth holder for our api keys."""

    def __init__(self, api_key):
        self.api_key = api_key
        self.user = api_key.user


def validate_api_key(api_key):
    if not api_key:
        raise AuthenticationFailed("Invalid API key")

    matching_key = models.ApiKey.objects.filter(key=api_key).first()
    if not matching_key:
        raise AuthenticationFailed("Invalid API key.")
    elif not matching_key.active:
        raise AuthenticationFailed("This API key is disabled.")
    elif matching_key.user and not matching_key.user.is_active:
        raise AuthenticationFailed("This user is disabled.")

    return (matching_key.user, ApiKeyAuthHolder(matching_key))


class ApiKeyBasicAuth(authentication.BasicAuthentication):
    """Authenticates using http basic, with username "api" and an api key as the password."""

    def authenticate_header(self, request):
        # Don't return a `WWW-Authenticate` header on auth fails.
        return None

    def authenticate_credentials(self, userid, password, request=None):
        if userid != "api" or not password:
            raise AuthenticationFailed(
                'For Basic Auth, provide "api" as the username and an API key as the password.'
            )
        return validate_api_key(password)
