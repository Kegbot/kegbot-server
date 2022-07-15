from django.conf import settings

from pykeg.core.util import get_current_request


class UnknownBaseUrlException(ValueError):
    pass


def get_base_url():
    """Returns the base URL of the site without a trailing slash.

    Result is used primarily in constructing absolute links back to the
    site, eg in notifications.
    """
    static_url = settings.KEGBOT["KEGBOT_BASE_URL"]
    if static_url:
        return static_url.rstrip("/")
    r = get_current_request()
    if not r:
        raise UnknownBaseUrlException("Cannot determine current request")
    return r.build_absolute_uri("/").rstrip("/")
