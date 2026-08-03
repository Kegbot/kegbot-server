"""Postgres-specific database backup/restore implementation."""

import logging
import os
import subprocess

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
        args.append("--username={}".format(params["user"]))
    if params.get("host"):
        args.append("--host={}".format(params["host"]))
    if params.get("port"):
        args.append("--port={}".format(params["port"]))
    return args


def common_env(params):
    env = dict(os.environ)
    if params.get("password"):
        env["PGPASSWORD"] = params["password"]
    return env


def engine_name():
    return "postgres"


def is_installed():
    params = db_params()
    args = ["psql"] + common_args(params)
    args += ["-qt", "-c \"select * from pg_tables where schemaname='public';\"", params["db"]]
    cmd = " ".join(args)
    logger.info(cmd)
    output = subprocess.check_output(cmd, env=common_env(params), shell=True, text=True)
    return "core_" in output


def dump(output_fd):
    params = db_params()
    args = ["pg_dump"] + common_args(params)
    args.append(params["db"])
    cmd = " ".join(args)
    logger.info(cmd)
    return subprocess.check_call(cmd, stdout=output_fd, env=common_env(params), shell=True)


def restore(input_fd):
    params = db_params()
    args = ["psql"] + common_args(params)
    args.append(params["db"])
    cmd = " ".join(args)
    logger.info(cmd)
    return subprocess.check_call(cmd, stdin=input_fd, env=common_env(params), shell=True)


def erase():
    params = db_params()
    args = ["psql"] + common_args(params)
    args += [params["db"], "-c 'drop schema public cascade; create schema public;'"]
    cmd = " ".join(args)
    logger.info(cmd)
    subprocess.check_call(cmd, env=common_env(params), shell=True)
