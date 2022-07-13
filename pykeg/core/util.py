"""Miscellaneous utility functions."""

# Note: imports should be limited to python stdlib, since methods here
# may be used in models.py, settings.py, etc.

import logging
import os
import pkgutil
import sys
import tempfile
from builtins import object, str
from collections import OrderedDict
from contextlib import closing
from distutils.version import StrictVersion
from importlib import metadata as importlib_metadata
from threading import current_thread

import requests
from django.core.exceptions import ImproperlyConfigured
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)

_REQUESTS = {}

DOCKER_VERSION_INFO_FILE = "/etc/kegbot-version"


def get_version():
    try:
        return importlib_metadata.version("kegbot")
    except importlib_metadata.PackageNotFoundError:
        return "0.0.0"


def get_version_object():
    return StrictVersion(get_version())


def must_upgrade(installed_version, new_version):
    # Compare major and minor (only).
    return installed_version.version[:2] < new_version.version[:2]


def should_upgrade(installed_verison, new_version):
    return installed_verison < new_version


def get_user_agent():
    return "KegbotServer/%s" % get_version()


def CtoF(t):
    return ((9.0 / 5.0) * t) + 32


def get_plugin_template_dirs(plugin_list):
    ret = []
    for plugin in plugin_list:
        plugin_module = ".".join(plugin.split(".")[:-1])
        pkg = pkgutil.get_loader(plugin_module)
        if not pkg:
            raise ImproperlyConfigured('Cannot find plugin "%s"' % plugin)
        template_dir = os.path.join(os.path.dirname(pkg.path), "templates")
        if os.path.isdir(template_dir):
            ret.append(template_dir)
    return ret


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
        logger.info("Downloading file %s to path %s" % (url, pathname))
        with closing(os.fdopen(fd, "wb")):
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    os.write(fd, chunk)
        return str(pathname)
    except requests.exceptions.RequestException as e:
        raise IOError("Could not download file: {}".format(e))


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


class SuppressTaskErrors(object):
    """Suppresses certain errors that occur while scheduling tasks."""

    def __init__(self, logger=None):
        self.logger = logger if logger else logging.getLogger(__name__)

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        exc_info = (exc_type, exc_val, exc_tb)
        if isinstance(exc_val, RedisError):
            self.logger.error("Error scheduling task: {}".format(exc_val), exc_info=exc_info)
            return True
        return False
