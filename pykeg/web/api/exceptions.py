"""Exception types for the legacy API, mapped to HTTP error responses."""


class Error(Exception):
    """An error occurred."""

    HTTP_CODE = 400

    def __init__(self, message=None):
        self.message = message

    def Message(self):
        if self.message:
            return self.message
        m = self.__class__.__doc__
        m = m.split("\n", 1)[0]
        return m


class NotFoundError(Error):
    """The requested object could not be found."""

    HTTP_CODE = 404


class ServerError(Error):
    """The server had a problem fulfilling your request."""

    HTTP_CODE = 500


class BadRequestError(Error):
    """The request was incomplete or malformed."""

    HTTP_CODE = 400


class NoAuthTokenError(Error):
    """An api_key is required."""

    HTTP_CODE = 401


class BadApiKeyError(Error):
    """The api_key given is invalid."""

    HTTP_CODE = 401


class PermissionDeniedError(Error):
    """The api_key given does not have permission for this resource."""

    HTTP_CODE = 401
