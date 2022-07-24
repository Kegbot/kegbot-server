"""Loads Kegbot configuration from env."""

import os
import sys

ENV_TEST = "test"
ENV_DEBUG = "debug"
ENV_PRODUCTION = "production"
ALL_ENVS = (ENV_TEST, ENV_DEBUG, ENV_PRODUCTION)

IS_RUNNING_PYTEST = "pytest" in sys.modules

ALL_SETTINGS = {}


def boolstr(val):
    return str(val).lower() == "true"


def valid_env(val):
    return val in ALL_ENVS


def Setting(name, default, typefn=str):
    if name in ALL_SETTINGS:
        raise ValueError("Bug: Setting {} registered more than once.".format(name))

    ALL_SETTINGS[name] = (default, typefn)


def get(name):
    val, typefn = ALL_SETTINGS[name]

    if name in os.environ:
        raw = os.environ.get(name)
        try:
            val = typefn(raw)
        except Exception as e:
            return None, e
    return val, None


def getvalue(name):
    val, err = get(name)
    if err:
        raise err
    return val


def all():
    ret = {}
    for name in ALL_SETTINGS:
        ret[name] = get(name)
    return ret


def all_values():
    ret = {}
    for name in ALL_SETTINGS:
        ret[name] = getvalue(name)
    return ret


def is_setup():
    return True


Setting("DATABASE_URL", os.getenv("DATABASE_URL", "mysql://root@localhost/kegbot"))
Setting("REDIS_URL", os.getenv("REDIS_URL", "redis://localhost:6379/0"))
Setting("KEGBOT_ENV", "test" if IS_RUNNING_PYTEST else ENV_DEBUG)
Setting("KEGBOT_BASE_URL", "http://test.example.com" if IS_RUNNING_PYTEST else "")
Setting("KEGBOT_EMAIL_FROM_ADDRESS", "")
Setting("KEGBOT_EMAIL_URL", os.getenv("EMAIL_URL", "smtp:"))
Setting("KEGBOT_DATA_DIR", "/kegbot-data")
Setting("KEGBOT_IN_DOCKER", False, typefn=boolstr)
Setting("KEGBOT_SECRET_KEY", "not-configured")
Setting("KEGBOT_INSECURE_SHARED_API_KEY", "")
Setting("KEGBOT_ENABLE_V2_API", True if IS_RUNNING_PYTEST else False, typefn=boolstr)
