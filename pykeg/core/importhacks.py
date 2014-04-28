#!/usr/bin/env python
#
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

import os
import sys
from pykeg.core.kb_common import LOCAL_SETTINGS_SEARCH_DIRS

_DEBUG = False

_CUSTOM_SEARCH_DIR = os.getenv('KEGBOT_SETTINGS_DIR')
if _CUSTOM_SEARCH_DIR:
    SEARCH_DIRS = [os.path.expanduser(_CUSTOM_SEARCH_DIR)]
else:
    SEARCH_DIRS = [os.path.expanduser(d) for d in LOCAL_SETTINGS_SEARCH_DIRS]


def _Debug(message):
    if _DEBUG:
        sys.stderr.write('importhacks: %s\n' % (message,))


def _Warning(message):
    if _DEBUG:
        sys.stderr.write('importhacks: %s\n' % (message,))


def _AddToSysPath(paths):
    for path in paths:
        path = os.path.abspath(path)
        if path not in sys.path:
            _Debug('Adding to sys.path: %s' % path)
            sys.path.append(path)
        else:
            _Debug('Already in sys.path: %s' % path)


def _ExtendSysPath():
    """ Add some paths where we'll look for user settings. """
    paths = []
    for dir in SEARCH_DIRS:
        paths.append(dir)
        if _DEBUG:
            test_settings = os.path.join(dir, 'local_settings.py')
            if os.path.exists(test_settings):
                _Debug('%s exists' % test_settings)
            else:
                _Debug('%s does NOT exist' % test_settings)

    _AddToSysPath(paths)


def _SetDjangoSettingsEnv(settings='pykeg.settings'):
    """ Set django settings if not set. """
    if not os.environ.get('DJANGO_SETTINGS_MODULE'):
        _Debug('Setting DJANGO_SETTINGS_MODULE=%s' % (settings,))
        os.environ['DJANGO_SETTINGS_MODULE'] = settings


def _FixAll():
    try:
        import pykeg
        pykeg_dir = os.path.dirname(pykeg.__file__)
        _Debug('Pykeg loaded from dir: %s' % pykeg_dir)
    except ImportError:
        _Warning('Error: pykeg could not be imported')
        sys.exit(1)

    _ExtendSysPath()
    _SetDjangoSettingsEnv()

    try:
        import local_settings
        common_dir = os.path.dirname(local_settings.__file__)
        _Debug('local_settings loaded from dir: %s' % common_dir)
    except ImportError:
        _Warning('Warning: local_settings could not be imported')

if __name__ == '__main__' or os.environ.get('DEBUG_IMPORT_HACKS'):
    # When run as a program, or DEBUG_IMPORT_HACKS is set: print debug info
    _DEBUG = True

_FixAll()
