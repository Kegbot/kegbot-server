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

"""Utilities for use in tests."""

import datetime
import os

from pykeg.backend.backends import KegbotBackend

from django.conf import settings
from django.utils import timezone

from django_nose import NoseTestSuiteRunner


TESTDATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../testdata/'))


def get_filename(f):
    return os.path.join(TESTDATA_DIR, f)


def make_datetime(*args):
    if settings.USE_TZ:
        return datetime.datetime(*args, tzinfo=timezone.utc)
    else:
        return datetime.datetime(*args)


class TestBackend(KegbotBackend):
    def get_base_url(self):
        static_url = getattr(settings, 'KEGBOT_BASE_URL', None)
        if static_url:
            return static_url.rstrip('/')
        return 'http://localhost:1234'


class KegbotTestSuiteRunner(NoseTestSuiteRunner):
    def __init__(self, *args, **kwargs):
        # Run all celery tasks synchronously.
        settings.CELERY_ALWAYS_EAGER = True
        super(KegbotTestSuiteRunner, self).__init__(*args, **kwargs)
