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

"""Unittests for the checkin module."""

from django.test import TransactionTestCase

from mock import Mock
from mock import patch

from pykeg.core import checkin
from pykeg.core import models
from pykeg.core.util import get_version


class CheckinTestCase(TransactionTestCase):

    def test_checkin(self):

        site = models.KegbotSite.get()
        site.registration_id = 'original-regid'
        site.save()

        version = get_version()

        with patch('requests.post') as mock_post:
            mock_post.return_value = mock_response = Mock()

            mock_response.status_code = 200
            mock_response.json.return_value = {
                'status': 'ok',
                'reg_id': 'new-regid'
            }
            checkin.checkin('http://example.com/checkin', 'test-product', 1.23)
            mock_post.assert_called_with('http://example.com/checkin',
                headers={'User-Agent': 'KegbotServer/%s' % version},
                data={
                    'reg_id': u'original-regid',
                    'product': 'test-product',
                    'version': version,
                },
                timeout=1.23)

        site = models.KegbotSite.get()
        self.assertEquals('new-regid', site.registration_id)
