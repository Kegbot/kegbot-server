# Copyright 2014 Bevbot LLC, All Rights Reserved
#
# This file is part of the Pykeg package of the Kegbot project.
# For more information on Pykeg or Kegbot, see http://kegbot.org/
#
# Pykeg is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# Pykeg is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pykeg.  If not, see <http://www.gnu.org/licenses/>.

"""MySQL-specific database backup/restore implementation."""

import logging
import subprocess

from django.conf import settings
from django.db.models import get_models

logger = logging.getLogger(__name__)

DEFAULT_DB = 'default'

# Common command-line arguments
PARAMS = {
    'db': settings.DATABASES[DEFAULT_DB].get('NAME'),
    'user': settings.DATABASES[DEFAULT_DB].get('USER'),
    'password': settings.DATABASES[DEFAULT_DB].get('PASSWORD'),
    'host': settings.DATABASES[DEFAULT_DB].get('HOST'),
    'port': settings.DATABASES[DEFAULT_DB].get('PORT'),
}

DEFAULT_ARGS = []
if PARAMS.get('user'):
    DEFAULT_ARGS.append('--user={}'.format(PARAMS['user']))
if PARAMS.get('password'):
    DEFAULT_ARGS.append('--password={}'.format(PARAMS['password']))
if PARAMS.get('host'):
    DEFAULT_ARGS.append('--host={}'.format(PARAMS['host']))
if PARAMS.get('port'):
    DEFAULT_ARGS.append('--port={}'.format(PARAMS['port']))


def engine_name():
    return 'mysql'


def is_installed():
    args = ['mysql', '--batch'] + DEFAULT_ARGS + [PARAMS['db']]
    args += ['-e', "'show tables like \"core_kegbotsite\";'"]

    cmd = ' '.join(args)
    logger.info('command: {}'.format(cmd))
    output = subprocess.check_output(cmd, shell=True)
    logger.info('result: {}'.format(output))
    return 'core_kegbotsite' in output


def dump(output_fd):
    args = ['mysqldump', '--skip-dump-date', '--single-transaction']
    if PARAMS.get('user'):
        args.append('--user={}'.format(PARAMS['user']))
    if PARAMS.get('password'):
        args.append('--password={}'.format(PARAMS['password']))
    if PARAMS.get('host'):
        args.append('--host={}'.format(PARAMS['host']))
    if PARAMS.get('port'):
        args.append('--port={}'.format(PARAMS['port']))

    args.append(PARAMS['db'])
    cmd = ' '.join(args)
    logger.info(cmd)
    return subprocess.check_call(cmd, stdout=output_fd, shell=True)


def restore(input_fd):
    args = ['mysql'] + DEFAULT_ARGS

    args.append(PARAMS['db'])
    cmd = ' '.join(args)
    logger.info(cmd)
    return subprocess.check_call(cmd, stdin=input_fd, shell=True)


def erase():
    args = ['mysql']
    if PARAMS.get('user'):
        args.append('--user={}'.format(PARAMS['user']))
    if PARAMS.get('password'):
        args.append('--password={}'.format(PARAMS['password']))
    if PARAMS.get('host'):
        args.append('--host={}'.format(PARAMS['host']))
    if PARAMS.get('port'):
        args.append('--port={}'.format(PARAMS['port']))

    args += [PARAMS['db']]

    # Build the sql command.
    tables = [str(model._meta.db_table) for model in get_models()]
    query = ["DROP TABLE IF EXISTS {};".format(t) for t in tables]
    query = ["SET FOREIGN_KEY_CHECKS=0;"] + query + ["SET FOREIGN_KEY_CHECKS=1;"]
    query = ' '.join(query)

    cmd = ' '.join(args + ['-e', "'{}'".format(query)])
    logger.info(cmd)
    subprocess.check_call(cmd, shell=True)
