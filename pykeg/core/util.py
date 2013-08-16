# Copyright 2013 Mike Wakerly <opensource@hoho.com>
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

"""Miscellaneous utility functions."""

# Note: imports should be limited to python stdlib, since methods here
# may be used in models.py, settings.py, etc.

from importlib import import_module
import os
import sys
import random

def make_serial():
    '''Returns a random serial number.'''
    return '%016x' % random.randrange(0, 2**64 - 1)

def get_plugin_template_dirs(plugin_list):
    from django.utils import six
    if not six.PY3:
        fs_encoding = sys.getfilesystemencoding() or sys.getdefaultencoding()

    ret = []
    for plugin in plugin_list:
        plugin_module = '.'.join(plugin.split('.')[:-1])
        try:
            mod = import_module(plugin_module)
        except ImportError as e:
            continue
        template_dir = os.path.join(os.path.dirname(mod.__file__), 'templates')
        if os.path.isdir(template_dir):
            if not six.PY3:
                template_dir = template_dir.decode(fs_encoding)
            ret.append(template_dir)
    return ret
