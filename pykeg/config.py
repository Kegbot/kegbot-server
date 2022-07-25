"""Loads Kegbot configuration from env."""

import os
import sys
import urllib

ENV_TEST = "test"
ENV_DEBUG = "debug"
ENV_PRODUCTION = "production"
ALL_ENVS = (ENV_TEST, ENV_DEBUG, ENV_PRODUCTION)

IS_RUNNING_PYTEST = "pytest" in sys.modules

# Registry if settings we understand. See `define_setting()`.
ALL_SETTINGS = {}


class ConfigError(Exception):
    """Base exception class."""


class MissingRequiredSetting(ConfigError):
    """Thrown when a required setting is missing."""


class MalformedSetting(ConfigError):
    """Thrown when a setting's value is malformed."""


def boolstr(val):
    return str(val).lower() in ("true", "1")


def uristr(val):
    parsed = urllib.parse.urlparse(val)
    if not parsed.scheme:
        raise ValueError(f"not a URI")
    return val


def valid_env(val):
    return val in ALL_ENVS


def define_setting(name, typefn=str, *, default, required):
    """Define a new setting.

    Args
        name: the name to search for in env
        typefn: a function which converts the env value to whatever it
            should be within the runtime
        default: the default value; may be None
        required: true if the setting _must_ be present in env
    """
    if name in ALL_SETTINGS:
        raise ValueError("Bug: Setting {} registered more than once.".format(name))

    ALL_SETTINGS[name] = (default, required, typefn)


def get(name):
    """Resolves a single setting from env.

    Will throw an exception if the value is malformed or if it is
    required and missing from env.
    """
    default_value, required, typefn = ALL_SETTINGS[name]

    if name in os.environ:
        raw = os.environ.get(name)
        try:
            val = typefn(raw)
            return val
        except (TypeError, ValueError) as e:
            raise MalformedSetting(f'The value for setting {name} is invalid: "{raw}" ({e})')
    elif required:
        raise MissingRequiredSetting(f"The setting {name} was not found in env, and is required.")

    return default_value


def all():
    """Resolves all settings from env, returning a dict."""
    ret = {}
    for name in ALL_SETTINGS:
        ret[name] = get(name)
    return ret


def validate(exit_on_error=True):
    """Validates env configuration.

    Upon error, if `exit_on_error` is true, the errors will be printed and the
    process will exit. Otherwise, a list of errors will be returned.
    """
    errors = []
    for setting_name in sorted(ALL_SETTINGS.keys()):
        try:
            get(setting_name)
        except ConfigError as e:
            errors.append((setting_name, e))
    if errors and exit_on_error:
        try:
            for setting_name, error in errors:
                print(f"Error: {error}", file=sys.stderr)
            print(
                f'Please fix the error{"s" if len(errors) > 1 else ""} above. Aborting.',
                file=sys.stderr,
            )
        finally:
            sys.exit(1)
    return errors


define_setting(
    "DATABASE_URL",
    default=os.getenv("DATABASE_URL", "mysql://root@localhost/kegbot"),
    typefn=uristr,
    required=True,
)

define_setting(
    "REDIS_URL",
    default=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    typefn=uristr,
    required=True,
)

define_setting("KEGBOT_SECRET_KEY", default=None, required=True)

define_setting("KEGBOT_ENV", default="test" if IS_RUNNING_PYTEST else ENV_DEBUG, required=False)

define_setting(
    "KEGBOT_BASE_URL",
    default="http://test.example.com" if IS_RUNNING_PYTEST else "",
    required=False,
)

define_setting("KEGBOT_DATA_DIR", default="/kegbot-data", required=False)

define_setting("KEGBOT_IN_DOCKER", default=False, typefn=boolstr, required=False)

define_setting("KEGBOT_INSECURE_SHARED_API_KEY", default="", required=False)

define_setting(
    "KEGBOT_ENABLE_V2_API",
    default=True if IS_RUNNING_PYTEST else False,
    typefn=boolstr,
    required=False,
)
