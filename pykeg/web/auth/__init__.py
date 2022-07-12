"""Kegbot authentication backend interface."""

from builtins import object

from django.contrib import auth
from django.core.exceptions import ImproperlyConfigured


def get_auth_backend():
    """Returns the sole authentication backend."""
    backends = auth.get_backends()
    if len(backends) != 1:
        raise ImproperlyConfigured("Expected exactly 1 backend (found {})".format(len(backends)))
    return backends[0]


class AuthException(Exception):
    """Top-level exception class."""


class UserExistsException(AuthException):
    """Registration error indicating this username/email is taken."""


class AuthBackend(object):

    # Django methods

    def authenticate(self, **credentials):
        raise NotImplementedError

    def get_user(self, user_id):
        raise NotImplementedError

    # Kegbot methods

    def is_manager(self, user):
        """Returns true if this user has manager privileges.

        True implies `is_member()` is also True.
        """
        raise NotImplementedError

    def set_is_manager(self, user, is_manager):
        """Sets or clears the manager status for this user."""
        raise NotImplementedError

    def is_owner(self, user):
        """Returns true if this user has owner privileges.

        True implies `is_manager()` is also True.
        """
        raise NotImplementedError

    def set_is_owner(self, user, is_owner):
        """Sets or clears the manager status for this user."""
        raise NotImplementedError

    def register(self, email, username, password=None, photo=None):
        """Registers a new user on this system.

        Args:
            email: new user's email address.
            username: desired username
            password: initial password
            photo: photo data

        Returns:
            The new User instance on success.
        """
        raise NotImplementedError
