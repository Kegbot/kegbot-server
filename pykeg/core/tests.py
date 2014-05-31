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

"""Generic unittests."""

import os
import subprocess

from django.test import TestCase
from django.utils.importlib import import_module


def path_for_import(name):
    """
    Returns the directory path for the given package or module.
    """
    return os.path.dirname(os.path.abspath(import_module(name).__file__))


class CoreTests(TestCase):

    def test_flake8(self):
        root_path = path_for_import('pykeg')
        command = 'flake8 {}'.format(root_path)
        try:
            subprocess.check_output(command.split())
        except subprocess.CalledProcessError as e:
            print 'command: {}'.format(command)
            print e.output
            self.fail('flake8 failed with return code {}.'.format(e.returncode))
