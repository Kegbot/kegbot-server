import multiprocessing
import os
import sys
from importlib import metadata as importlib_metadata

BANNER = """
██╗  ██╗███████╗ ██████╗ ██████╗  ██████╗ ████████╗
██║ ██╔╝██╔════╝██╔════╝ ██╔══██╗██╔═══██╗╚══██╔══╝
█████╔╝ █████╗  ██║  ███╗██████╔╝██║   ██║   ██║   
██╔═██╗ ██╔══╝  ██║   ██║██╔══██╗██║   ██║   ██║   
██║  ██╗███████╗╚██████╔╝██████╔╝╚██████╔╝   ██║   
╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝  ╚═════╝    ╚═╝   
""".strip()


def get_version():
    try:
        return importlib_metadata.version("kegbot")
    except importlib_metadata.PackageNotFoundError:
        return "0.0.0"


if os.getenv("KEGBOT_IN_HEROKU") and os.getenv("PORT"):
    # Necessary on Heroku, which doesn't respect EXPOSE :-\
    bind = "0.0.0.0:{}".format(int(os.getenv("PORT")))
else:
    bind = "0.0.0.0:8000"

worker_class = "gevent"
workers = multiprocessing.cpu_count() * 2 + 1

print(BANNER, file=sys.stderr)
print("kegbot-server - version {}".format(get_version()), file=sys.stderr)
print("  homepage: https://kegbot.org", file=sys.stderr)
print("   discuss: https://forum.kegbot.org", file=sys.stderr)
print("-" * 80, file=sys.stderr)
