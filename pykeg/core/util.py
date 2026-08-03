"""Miscellaneous utility functions."""

# Note: imports should be limited to python stdlib, since methods here
# may be used in models.py, settings.py, etc.

import logging
import os
import tempfile
from collections import OrderedDict
from contextlib import closing
from importlib import metadata as importlib_metadata
from importlib.metadata import version
from threading import current_thread

import requests
from packaging.version import Version
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)

_REQUESTS = {}

DOCKER_VERSION_INFO_FILE = "/etc/kegbot-version"


def get_version():
    try:
        return version("kegbot")
    except importlib_metadata.PackageNotFoundError:
        return "0.0.0"


def get_version_object():
    return Version(get_version())


def must_upgrade(installed_version, new_version):
    # Compare major and minor (only).
    return installed_version.release[:2] < new_version.release[:2]


def should_upgrade(installed_verison, new_version):
    return installed_verison < new_version


def get_user_agent():
    return f"KegbotServer/{get_version()}"


def CtoF(t):
    return ((9.0 / 5.0) * t) + 32


def get_current_request():
    """Retrieve the current request.

    Adapted from: http://nedbatchelder.com/blog/201008/global_django_requests.html
    """
    return _REQUESTS.get(current_thread())


def set_current_request(request):
    thr = current_thread()
    if request:
        _REQUESTS[thr] = request
    else:
        if thr in _REQUESTS:
            del _REQUESTS[thr]


def download_to_tempfile(url):
    try:
        r = requests.get(url, stream=True)
        ext = os.path.splitext(url)[1]
        fd, pathname = tempfile.mkstemp(suffix=ext)
        logger.info(f"Downloading file {url} to path {pathname}")
        with closing(os.fdopen(fd, "wb")):
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    os.write(fd, chunk)
        return str(pathname)
    except requests.exceptions.RequestException as e:
        raise OSError(f"Could not download file: {e}")


def get_runtime_version_info():
    ret = {}
    if os.environ.get("KEGBOT_IN_DOCKER") and os.path.exists(DOCKER_VERSION_INFO_FILE):
        with open(DOCKER_VERSION_INFO_FILE) as f:
            for line in f:
                if not line.strip() or "=" not in line:
                    continue
                key, val = line.strip().split("=")
                ret[key] = val
    return OrderedDict(sorted(ret.items()))


class SuppressTaskErrors:
    """Suppresses certain errors that occur while scheduling tasks."""

    def __init__(self, logger=None):
        self.logger = logger if logger else logging.getLogger(__name__)

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        exc_info = (exc_type, exc_val, exc_tb)
        if isinstance(exc_val, RedisError):
            self.logger.error(f"Error scheduling task: {exc_val}", exc_info=exc_info)
            return True
        return False
