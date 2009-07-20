#!/usr/bin/env python
#
# Copyright 2009 Mike Wakerly <opensource@hoho.com>
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

### Extend PYTHONPATH so we can load settings from it

SYSTEM_SETTINGS_DIR = "/etc/kegbot"
HOME_DIR = os.environ.get('HOME')
USER_SETTINGS_DIR = os.path.join(HOME_DIR, '.kegbot')

# Greatest precedence: $HOME/.kegbot/
if USER_SETTINGS_DIR not in sys.path:
  sys.path.append(USER_SETTINGS_DIR)

# Next precedence: /etc/kegbot
if SYSTEM_SETTINGS_DIR not in sys.path:
  sys.path.append(SYSTEM_SETTINGS_DIR)

### Set django settings if not set

if not os.environ.get('DJANGO_SETTINGS_MODULE'):
  os.environ['DJANGO_SETTINGS_MODULE'] = 'pykeg.settings'

### Extend the python path if import fails

try:
  import pykeg
except ImportError:
  _local_dir = os.path.dirname(sys.modules[__name__].__file__)
  _package_dir = os.path.normpath(os.path.join(_local_dir, '../..'))
  print 'Adding to PYTHONPATH:', _package_dir
  sys.path.append(_package_dir)

