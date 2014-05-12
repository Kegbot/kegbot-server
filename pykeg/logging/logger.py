"""Redis logging utilities.

Adopted from python-redis-log under the following license:

    Copyright (c) 2011 Jed Parsons <jedp@jedparsons.com>

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    THE SOFTWARE.

Local changes:
    - Added get_current_request() in _getCallingContext()
    - Added request_info in RedisLogRecord
"""

import socket
import getpass
import datetime
import inspect
import logging

from pykeg.core.util import get_current_request


def levelAsString(level):
    return {logging.DEBUG: 'debug',
            logging.INFO: 'info',
            logging.WARNING: 'warning',
            logging.ERROR: 'error',
            logging.CRITICAL: 'critical',
            logging.FATAL: 'fatal'}.get(level, 'unknown')


def _getCallingContext():
    """
    Utility function for the RedisLogRecord.

    Returns the module, function, and lineno of the function
    that called the logger.

    We look way up in the stack.  The stack at this point is:
    [0] logger.py _getCallingContext (hey, that's me!)
    [1] logger.py __init__
    [2] logger.py makeRecord
    [3] _log
    [4] <logging method>
    [5] caller of logging method
    """
    frames = inspect.stack()

    if len(frames) > 4:
        context = frames[5]
    else:
        context = frames[0]

    modname = context[1]
    lineno = context[2]

    if context[3]:
        funcname = context[3]
    else:
        funcname = ""

    request = get_current_request()

    # python docs say you don't want references to
    # frames lying around.  Bad things can happen.
    del context
    del frames

    return modname, funcname, lineno, request


class RedisLogRecord(logging.LogRecord):
    def __init__(self, name, lvl, fn, lno, msg, args, exc_info, func=None, extra=None):
        logging.LogRecord.__init__(self, name, lvl, fn, lno, msg, args, exc_info, func)

        # You can also access the following instance variables via the
        # formatter as
        #     %(hostname)s
        #     %(username)s
        #     %(modname)s
        # etc.
        self.hostname = socket.gethostname()
        self.username = getpass.getuser()
        self.modname, self.funcname, self.lineno, request = _getCallingContext()

        self._raw = {
            'name': name,
            'level': levelAsString(lvl),
            'filename': fn,
            'line_no': self.lineno,
            'msg': unicode(msg),
            'args': list(args),
            'time': datetime.datetime.utcnow(),
            'username': self.username,
            'funcname': self.funcname,
            'hostname': self.hostname,
            'traceback': exc_info,
            'request_info': self._request_info(request),
        }

    def _request_info(self, request):
        """Extracts loggable information from a request."""
        ret = {}
        if not request or not hasattr(request, 'META'):
            return ret
        ret['addr'] = request.META.get('REMOTE_ADDR')
        ret['request_path'] = request.path
        ret['method'] = request.method
        return ret


class RedisLogger(logging.getLoggerClass()):
    def makeRecord(self, name, lvl, fn, lno, msg, args, exc_info, func=None, extra=None):
        record = RedisLogRecord(name, lvl, fn, lno, msg, args, exc_info, func=None)

        if extra:
            for key in extra:
                if (key in ["message", "asctime"]) or (key in record.__dict__):
                    raise KeyError("Attempt to overwrite %r in RedisLogRecord" % key)
                record.__dict__[key] = extra[key]
        return record
