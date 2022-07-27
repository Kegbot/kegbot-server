import datetime
import json
import os
import subprocess
import sys

import isodate
import redis

from pykeg.core.util import get_version

SEPARATOR = "-" * 100 + "\n"


def writeline(fd, data):
    fd.write(data)
    fd.write("\n")
    fd.flush()


def writepair(fd, a, b):
    fd.write("  ")
    fd.write(a)
    fd.write(": ")
    fd.write(b)
    fd.write("\n")


def writelog(fd, log):
    writeline(fd, "--- {}\t{}\t{}".format(log.get("time"), log.get("name"), log.get("msg")))

    request_info = log.get("request_info")
    if request_info:
        method = request_info.get("method")
        path = request_info.get("request_path")
        addr = request_info.get("addr")
        writeline(fd, "    * Request: {} {} ({})".format(method, path, addr))

    traceback = log.get("traceback")
    if traceback:
        indent = " " * 6
        fd.write("    * ")
        # writeline(fd, '    * Traceback')
        traceback = traceback.replace("\n", "\n" + indent)
        writeline(fd, traceback)
        writeline(fd, "")


def get_output(cmd):
    try:
        return (
            subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
            .decode("utf-8")
            .strip()
        )
    except subprocess.CalledProcessError as e:
        return "ERR ({})".format(e)


def bugreport(fd):
    now = datetime.datetime.now()
    writeline(fd, "Kegbot Server {} Bugreport".format(get_version()))
    writeline(fd, "Generated {}".format(isodate.datetime_isoformat(now)))

    fd.write(SEPARATOR)
    writeline(fd, "## System info\n")
    writepair(fd, "kegbot path", get_output("which kegbot"))
    writepair(fd, "python bin path", get_output("which python"))
    writeline(fd, "\n")

    fd.write(SEPARATOR)
    writeline(fd, "## Environment\n")
    for k in sorted(os.environ):
        writepair(fd, k, os.environ[k])
    writeline(fd, "\n")

    fd.write(SEPARATOR)
    writeline(fd, "## `cat /etc/kegbot-version` output\n")
    writeline(fd, get_output("cat /etc/kegbot-version"))
    writeline(fd, "\n")

    fd.write(SEPARATOR)
    writeline(fd, "## `pip freeze` output\n")
    writeline(fd, get_output("pip freeze"))
    writeline(fd, "\n")

    fd.write(SEPARATOR)
    writeline(fd, "## `kegbot showmigrations` output\n")
    writeline(fd, get_output("kegbot showmigrations --no-color"))
    writeline(fd, "\n")

    fd.write(SEPARATOR)
    writeline(fd, "## kegbot logs\n")
    try:
        r = redis.Redis.from_url(os.getenv("REDIS_URL") or "redis://")
        logs = r.lrange("kb:log", 0, -1)
        for log in logs:
            try:
                log = json.loads(log)
            except ValueError:
                continue
            writelog(fd, log)
    except redis.RedisError as e:
        writeline(fd, "ERR ({})".format(e))
    writeline(fd, "\n")

    fd.write(SEPARATOR)
    writeline(fd, "WARNING: There may be secrets/passwords above! Use caution if sharing.")
    writeline(fd, "\\m/ End of bugreport \\m/")


def take_bugreport():
    bugreport(sys.stdout)
    print("")
    return 0


if __name__ == "__main__":
    sys.exit(take_bugreport())
