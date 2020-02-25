# Copyright 2014 Kegbot Project contributors
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

"""Utilities for use in tests."""

import datetime
import os

from pykeg.backend.backends import KegbotBackend

from django.conf import settings
from django.utils import timezone

import vcr

TESTDATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../testdata/'))
CASSETTE_DIR = os.path.join(TESTDATA_DIR, 'request_fixtures')


def get_filename(f):
    return os.path.join(TESTDATA_DIR, f)


def make_datetime(*args):
    if settings.USE_TZ:
        return datetime.datetime(*args, tzinfo=timezone.utc)
    else:
        return datetime.datetime(*args)


def get_vcr(test_name):
    cassette_dir = os.path.join(CASSETTE_DIR, test_name)
    return vcr.VCR(
        serializer='yaml',
        cassette_library_dir=cassette_dir,
        record_mode='none',
        match_on=['uri', 'method'],
    )


class TestBackend(KegbotBackend):
    def get_base_url(self):
        static_url = getattr(settings, 'KEGBOT_BASE_URL', None)
        if static_url:
            return static_url.rstrip('/')
        return 'http://localhost:1234'

