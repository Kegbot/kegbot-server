"""Kegweb API exceptions.

These are re-exported here so server code can `from pykeg.proto import kbapi`
and reference e.g. `kbapi.NoAuthTokenError`. The old gflags-based HTTP client
lived here too; it was unused by the server and now lives in the kegbot-api
project.
"""

from .exceptions import (
    BadApiKeyError,
    BadRequestError,
    Error,
    ErrorCodeToException,
    NoAuthTokenError,
    NotFoundError,
    PermissionDeniedError,
    RequestError,
    ServerError,
)

__all__ = [
    "BadApiKeyError",
    "BadRequestError",
    "Error",
    "ErrorCodeToException",
    "NoAuthTokenError",
    "NotFoundError",
    "PermissionDeniedError",
    "RequestError",
    "ServerError",
]
