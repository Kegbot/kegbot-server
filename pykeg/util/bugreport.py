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

from cStringIO import StringIO
import datetime
import isodate
import json
import os
import redis
import requests
import stat
import subprocess
import sys
from pykeg.core.util import get_version


SEPARATOR = '-' * 72 + '\n'


def writeline(fd, data):
    fd.write(data)
    fd.write('\n')
    fd.flush()


def writepair(fd, a, b):
    fd.write('  ')
    fd.write(a)
    fd.write(': ')
    fd.write(b)
    fd.write('\n')


def writelog(fd, log):
    writeline(fd, '--- {}\t{}\t{}'.format(log.get('time'), log.get('name'), log.get('msg')))

    request_info = log.get('request_info')
    if request_info:
        method = request_info.get('method')
        path = request_info.get('request_path')
        addr = request_info.get('addr')
        writeline(fd, '    * Request: {} {} ({})'.format(method, path, addr))

    traceback = log.get('traceback')
    if traceback:
        indent = ' ' * 6
        fd.write('    * ')
        # writeline(fd, '    * Traceback')
        traceback = traceback.replace('\n', '\n' + indent)
        writeline(fd, traceback)
        writeline(fd, '')


def get_output(cmd):
    try:
        return subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True).strip()
    except subprocess.CalledProcessError as e:
        return 'ERR ({})'.format(e)


def bugreport(fd):
    now = datetime.datetime.now()
    writeline(fd, 'Kegbot Server {} Bugreport'.format(get_version()))
    writeline(fd, 'Generated {}'.format(isodate.datetime_isoformat(now)))

    fd.write(SEPARATOR)
    writeline(fd, '## System info\n')
    writepair(fd, 'kegbot path', get_output('which kegbot'))
    writepair(fd, 'python bin path', get_output('which python'))
    writeline(fd, '\n')

    fd.write(SEPARATOR)
    writeline(fd, '## Environment\n')
    for k in sorted(os.environ):
        writepair(fd, k, os.environ[k])
    writeline(fd, '\n')

    fd.write(SEPARATOR)
    writeline(fd, '## `pip freeze` output\n')
    writeline(fd, get_output('pip freeze'))
    writeline(fd, '\n')

    fd.write(SEPARATOR)
    writeline(fd, '## `kegbot migrate --list` output\n')
    writeline(fd, get_output('kegbot migrate --list --no-color --noinput'))
    writeline(fd, '\n')

    fd.write(SEPARATOR)
    writeline(fd, '## kegbot logs\n')
    try:
        r = redis.Redis()
        logs = r.lrange('kb:log', 0, -1)
        for log in logs:
            try:
                log = json.loads(log)
            except ValueError:
                continue
            writelog(fd, log)
    except redis.RedisError as e:
        writeline(fd, 'ERR ({})'.format(e))
    writeline(fd, '\n')

    fd.write(SEPARATOR)
    writeline(fd, '\\m/ End of bugreport \\m/')


def should_prompt():
    if '--noinput' in sys.argv:
        return False

    mode = os.fstat(sys.stdin.fileno()).st_mode
    if stat.S_ISFIFO(mode):
        return False
    elif stat.S_ISREG(mode):
        return False
    else:
        return True


def prompt_to_post():
    sys.stderr.write('Bugreport collected!\n\n')

    sys.stderr.write('Because bugreports can be quite large, we recommend posting it to\n')
    sys.stderr.write('a pastebin rather than sharing directly on the Kegbot forum.\n\n')

    sys.stderr.write('dpaste.com is a semi-public pastebin for sharing text files, which\n')
    sys.stderr.write('this tool can automatically upload to. Please review the bugreport\n')
    sys.stderr.write('for sensitive information before deciding to post.\n\n')

    while True:
        sys.stderr.write('Post this bugreport to dpaste.com for easy sharing (y/n)? ')
        val = raw_input()
        val = val.strip().lower()
        if not val or val[0] not in ('y', 'n'):
            sys.stderr.write('Please type "y" or "n" to continue.\n')
            continue
        break
    return val[0] == 'y'


def post_report(value):
    response = requests.post('http://dpaste.com/api/v2/',
        data={'content': value}, allow_redirects=False)
    result = response.headers.get('location', 'unknown')
    return result


def take_bugreport():
    prompt = should_prompt()

    if prompt:
        fd = StringIO()
    else:
        fd = sys.stdout

    try:
        bugreport(fd)

        if prompt:
            val = fd.getvalue()
            print val
            print ''
            if prompt_to_post():
                url = post_report(val)
                sys.stderr.write('Bugreport posted: {}\n'.format(url))
        return 0
    except KeyboardInterrupt:
        sys.stderr.write("\nAlrighty then, I'll leave you alone...\n")
        return 1


if __name__ == '__main__':
    sys.exit(take_bugreport())
