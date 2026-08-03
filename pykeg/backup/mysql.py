"""MySQL-specific database backup/restore implementation."""

import logging
import subprocess

from django.apps import apps
from django.conf import settings

logger = logging.getLogger(__name__)

DEFAULT_DB = "default"

# Common command-line arguments
PARAMS = {
    "db": settings.DATABASES[DEFAULT_DB].get("NAME"),
    "user": settings.DATABASES[DEFAULT_DB].get("USER"),
    "password": settings.DATABASES[DEFAULT_DB].get("PASSWORD"),
    "host": settings.DATABASES[DEFAULT_DB].get("HOST"),
    "port": settings.DATABASES[DEFAULT_DB].get("PORT"),
}

DEFAULT_ARGS = []
if PARAMS.get("user"):
    DEFAULT_ARGS.append("--user={}".format(PARAMS["user"]))
if PARAMS.get("password"):
    DEFAULT_ARGS.append("--password={}".format(PARAMS["password"]))
if PARAMS.get("host"):
    DEFAULT_ARGS.append("--host={}".format(PARAMS["host"]))
if PARAMS.get("port"):
    DEFAULT_ARGS.append("--port={}".format(PARAMS["port"]))

# MariaDB 11.4+ clients verify server certificates by default, which fails
# against the self-signed certs MySQL servers auto-generate. Keep TLS but
# skip verification, matching how the Django connection behaves. The
# "loose-" prefix makes clients without this option (Oracle mysql) warn
# instead of exit.
DEFAULT_ARGS.append("--loose-ssl-verify-server-cert=0")


def engine_name():
    return "mysql"


def is_installed():
    args = ["mysql", "--batch"] + DEFAULT_ARGS + [PARAMS["db"]]
    args += ["-e", "'show tables like \"core_kegbotsite\";'"]

    cmd = " ".join(args)
    logger.info(f"command: {cmd}")
    output = subprocess.check_output(cmd, shell=True, text=True)
    logger.info(f"result: {output}")
    return "core_kegbotsite" in output


def dump(output_fd):
    args = ["mysqldump", "--skip-dump-date", "--single-transaction"] + DEFAULT_ARGS
    args.append(PARAMS["db"])
    cmd = " ".join(args)
    logger.info(cmd)
    return subprocess.check_call(cmd, stdout=output_fd, shell=True)


def restore(input_fd):
    args = ["mysql"] + DEFAULT_ARGS

    args.append(PARAMS["db"])
    cmd = " ".join(args)
    logger.info(cmd)
    return subprocess.check_call(cmd, stdin=input_fd, shell=True)


def erase():
    args = ["mysql"] + DEFAULT_ARGS + [PARAMS["db"]]

    # Build the sql command.
    tables = [str(model._meta.db_table) for model in apps.get_models()]
    query = [f"DROP TABLE IF EXISTS {t};" for t in tables]
    query = ["SET FOREIGN_KEY_CHECKS=0;"] + query + ["SET FOREIGN_KEY_CHECKS=1;"]
    query = " ".join(query)

    cmd = " ".join(args + ["-e", f"'{query}'"])
    logger.info(cmd)
    subprocess.check_call(cmd, shell=True)
