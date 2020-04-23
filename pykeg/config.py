"""Loads Kegbot configuration from env or config files.
"""

import configparser
import os
import sys

SOURCE_ENV = "env"
SOURCE_FILE = "file"
SOURCE_DEFAULT = "default"

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


def read_config(filename=None):
    if not filename:
        filename = os.path.join(getvalue("KEGBOT_DATA_DIR"), "kegbot.cfg")
    config = configparser.ConfigParser()
    try:
        with open(filename) as fp:
            config.readfp(fp)
        return dict((i[0].upper(), i[1]) for i in config.items("config"))
    except IOError:
        return {}


def get(name):
    default, typefn = ALL_SETTINGS[name]

    if name in os.environ or name == "KEGBOT_DATA_DIR":
        raw = os.environ.get(name, None)
        if raw is None:
            val, err, source = default, None, SOURCE_DEFAULT
        else:
            try:
                val, err, source = typefn(raw), None, SOURCE_ENV
            except Exception as e:
                val, err, source = None, e, SOURCE_ENV
    else:
        try:
            config = read_config()
            raw = config.get(name)
            if raw is None:
                val, err, source = default, None, SOURCE_DEFAULT
            else:
                val, err, source = typefn(raw), None, SOURCE_FILE
        except Exception as e:
            val, err, source = None, e, SOURCE_FILE
    return val, err, source


def getvalue(name):
    val, err, _ = get(name)
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


Setting("KEGBOT_ENV", "test" if IS_RUNNING_PYTEST else ENV_DEBUG)
Setting("KEGBOT_EMAIL_FROM_ADDRESS", "")
Setting("KEGBOT_DATA_DIR", "/kegbot-data")
Setting("KEGBOT_IN_DOCKER", False, typefn=boolstr)
Setting("KEGBOT_SECRET_KEY", "not-configured")
Setting("KEGBOT_SETUP_ENABLED", False, typefn=boolstr)
Setting("KEGBOT_DATABASE_URL", os.getenv("DATABASE_URL", "mysql://root@localhost/kegbot"))
Setting("KEGBOT_REDIS_URL", os.getenv("REDIS_URL", "redis://localhost:6379/0"))
