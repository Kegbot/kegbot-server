"""Dev-server override: default to port 8001.

In development the vite dev server owns http://localhost:8000 (the
address you actually browse to) and proxies backend paths here. This
command must live in an app listed *before* whitenoise.runserver_nostatic
in INSTALLED_APPS so it takes precedence; it subclasses whitenoise's
command, which in turn wraps the next-lower-priority runserver.
"""

from whitenoise.runserver_nostatic.management.commands.runserver import (
    Command as RunserverNostaticCommand,
)


class Command(RunserverNostaticCommand):
    default_port = "8001"
