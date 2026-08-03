"""MySQL-specific database backup/restore implementation."""

import logging
import subprocess

from django.apps import apps
from django.conf import settings

logger = logging.getLogger(__name__)

DEFAULT_DB = "default"


def db_params():
    """Reads connection parameters lazily: under test, the database name is
    swapped for the test database after this module is imported."""
    db = settings.DATABASES[DEFAULT_DB]
    return {
        "db": db.get("NAME"),
        "user": db.get("USER"),
        "password": db.get("PASSWORD"),
        "host": db.get("HOST"),
        "port": db.get("PORT"),
    }


def common_args(params):
    args = []
    if params.get("user"):
        args.append("--user={}".format(params["user"]))
    if params.get("password"):
        args.append("--password={}".format(params["password"]))
    if params.get("host"):
        args.append("--host={}".format(params["host"]))
    if params.get("port"):
        args.append("--port={}".format(params["port"]))

    # MariaDB 11.4+ clients verify server certificates by default, which
    # fails against the self-signed certs MySQL servers auto-generate. Keep
    # TLS but skip verification, matching how the Django connection behaves.
    # The "loose-" prefix makes clients without this option (Oracle mysql)
    # warn instead of exit.
    args.append("--loose-ssl-verify-server-cert=0")
    return args


def engine_name():
    return "mysql"


def is_installed():
    params = db_params()
    args = ["mysql", "--batch"] + common_args(params) + [params["db"]]
    args += ["-e", "'show tables like \"core_kegbotsite\";'"]

    cmd = " ".join(args)
    logger.info(f"command: {cmd}")
    output = subprocess.check_output(cmd, shell=True, text=True)
    logger.info(f"result: {output}")
    return "core_kegbotsite" in output


def dump(output_fd):
    params = db_params()
    args = ["mysqldump", "--skip-dump-date", "--single-transaction"] + common_args(params)
    args.append(params["db"])
    cmd = " ".join(args)
    logger.info(cmd)
    return subprocess.check_call(cmd, stdout=output_fd, shell=True)


def restore(input_fd):
    params = db_params()
    args = ["mysql"] + common_args(params) + [params["db"]]
    cmd = " ".join(args)
    logger.info(cmd)
    return subprocess.check_call(cmd, stdin=input_fd, shell=True)


def erase():
    params = db_params()
    args = ["mysql"] + common_args(params) + [params["db"]]

    # Build the sql command.
    tables = [str(model._meta.db_table) for model in apps.get_models()]
    query = [f"DROP TABLE IF EXISTS {t};" for t in tables]
    query = ["SET FOREIGN_KEY_CHECKS=0;"] + query + ["SET FOREIGN_KEY_CHECKS=1;"]
    query = " ".join(query)

    cmd = " ".join(args + ["-e", f"'{query}'"])
    logger.info(cmd)
    subprocess.check_call(cmd, shell=True)
