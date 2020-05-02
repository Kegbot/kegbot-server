class BackendError(Exception):
    """Base backend error exception."""


class NoTokenError(BackendError):
    """Token given is unknown."""


class UserExistsError(BackendError):
    """A user with this username already exists."""
