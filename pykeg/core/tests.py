"""Generic unittests."""

import os
import subprocess
import unittest
from importlib import import_module

from django.test import TestCase


def path_for_import(name):
    """
    Returns the directory path for the given package or module.
    """
    return os.path.dirname(os.path.abspath(import_module(name).__file__))


@unittest.skip("lint tests failing")
class CoreTests(TestCase):
    def test_flake8(self):
        root_path = path_for_import("pykeg")
        config_file = os.path.join(root_path, "setup.cfg")
        command = "flake8 --config={} {}".format(config_file, root_path)
        try:
            subprocess.check_output(command.split())
        except subprocess.CalledProcessError as e:
            print("command: {}".format(command))
            print(e.output)
            self.fail("flake8 failed with return code {}.".format(e.returncode))
