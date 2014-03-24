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

"""Unittests for pykeg.web.api"""

from django.test import TransactionTestCase
from pykeg.core import models
from pykeg.core import defaults
from kegbot.util import kbjson

### Helper methods

def create_site():
    return defaults.set_defaults(set_is_setup=True)

class BaseApiTestCase(TransactionTestCase):
    def get(self, subpath, data={}, follow=False, **extra):
        response = self.client.get('/api/%s' % subpath, data=data, follow=follow,
            **extra)
        return response, kbjson.loads(response.content)

class ApiClientTestCase(BaseApiTestCase):
    def testNotSetUp(self):
        '''Api endpoints should all error out prior to site setup.'''

        endpoints = ('events/', 'taps/', 'kegs/')
        for endpoint in endpoints:
            response, data = self.get(endpoint)
            self.assertEquals(data.meta.result, 'error')
            self.assertEquals(data.error.code, 'BadRequestError')

        create_site()

        # Ordinary results expected after site installed.
        for endpoint in endpoints:
            response, data = self.get(endpoint)
            self.assertEquals(data.meta.result, 'ok')

    def testSiteDefaults(self):
        create_site()

        empty_endpoints = ('events/', 'kegs/')
        for endpoint in empty_endpoints:
            response, data = self.get(endpoint)
            self.assertEquals(data.objects, [])

        response, data = self.get('taps/')
        taps = data.objects
        self.assertEquals(2, len(taps))
        self.assertEquals('Main Tap', taps[0].name)
        self.assertEquals('kegboard.flow0', taps[0].meter_name)
        self.assertEquals('Second Tap', taps[1].name)
        self.assertEquals('kegboard.flow1', taps[1].meter_name)

        for tap in taps:
            response1, data1 = self.get('taps/%s' % tap.meter_name)
            self.assertEquals(data1.meta.result, 'ok')
            
            response2, data2 = self.get('taps/%s' % tap.id)
            self.assertEquals(data2.meta.result, 'ok')

            self.assertEquals(data1, data2)

    def testApiAccess(self):
        site = create_site()

        protected_get_endpoints = ('users/',)

        user = models.User.objects.create(username='testuser')
        user.set_password('testpass')
        user.save()

        endpoint = 'users/'

        # No API key.
        response, data = self.get(endpoint)
        self.assertEquals(data.meta.result, 'error')
        self.assertEquals(data.error.code, 'NoAuthTokenError')

        # Non-existent key.
        response, data = self.get(endpoint, HTTP_X_KEGBOT_API_KEY='123')
        self.assertEquals(data.meta.result, 'error')
        self.assertEquals(data.error.code, 'BadApiKeyError')

        api_key_obj = models.ApiKey.objects.create(user=user, key='123')

        # Key exists, but non-superuser.
        response, data = self.get(endpoint, HTTP_X_KEGBOT_API_KEY='123')
        self.assertEquals(data.meta.result, 'error')
        self.assertEquals(data.error.code, 'PermissionDeniedError')

        user.is_staff = True
        user.save()

        # Finally ok.
        response, data = self.get(endpoint, HTTP_X_KEGBOT_API_KEY='123')
        self.assertEquals(data.meta.result, 'ok')

        endpoint = 'events/'

        # Alter privacy and compare.
        response, data = self.get(endpoint)
        self.assertEquals(data.meta.result, 'ok')
        site.settings.privacy = 'members'
        site.settings.save()

        response, data = self.get(endpoint)
        self.assertEquals(data.meta.result, 'error')

        self.client.login(username='testuser', password='testpass')
        response, data = self.get(endpoint)
        self.assertEquals(data.meta.result, 'ok')

        # Alert to staff-only.
        site.settings.privacy = 'staff'
        site.settings.save()
        response, data = self.get(endpoint)
        self.assertEquals(data.meta.result, 'ok')

        user.is_staff = False
        user.save()
        response, data = self.get(endpoint)
        self.assertEquals(data.meta.result, 'error')
        self.assertEquals(data.error.code, 'NoAuthTokenError')

    def test_controller_data(self):
        site = create_site()
        user = models.User.objects.create(username='testuser', is_staff=True)
        api_key_obj = models.ApiKey.objects.create(user=user, key='123')
        api_key = api_key_obj.key

        for endpoint in ('controllers', 'flow-meters'):
            response, data = self.get(endpoint)
            self.assertEquals(data.meta.result, 'error')
            self.assertEquals(data.error.code, 'NoAuthTokenError')

        response, data = self.get('controllers', HTTP_X_KEGBOT_API_KEY='123')
        self.assertEquals(data.meta.result, 'ok')
        expected = {
            'objects': [
                {
                    'id': 1,
                    'name': 'kegboard',
                }
            ],
            'meta': {
                'result': 'ok',
            }
        }
        self.assertEquals(expected, data)

        response, data = self.get('flow-meters', HTTP_X_KEGBOT_API_KEY='123')
        self.assertEquals(data.meta.result, 'ok')
        expected = {
            'objects': [
                {
                    'id': 1,
                    'ticks_per_ml': 5.4,
                    'port_name': 'flow0',
                    'controller': {
                        'id': 1,
                        'name': 'kegboard',
                    },
                    'name': 'kegboard.flow0'
                },
                {
                    'id': 2,
                    'ticks_per_ml': 5.4,
                    'port_name': 'flow1',
                    'controller': {
                        'id': 1,
                        'name': 'kegboard'
                    },
                    'name': 'kegboard.flow1'
                },
            ],
            'meta': { 'result': 'ok'}
        }
        self.assertEquals(expected, data)

        response, data = self.get('flow-toggles', HTTP_X_KEGBOT_API_KEY='123')
        self.assertEquals(data.meta.result, 'ok')
        expected = {
            'objects': [
                {
                    'id': 1,
                    'port_name': 'relay0',
                    'controller': {
                        'id': 1,
                        'name': 'kegboard',
                    },
                    'name': 'kegboard.relay0'
                },
                {
                    'id': 2,
                    'port_name': 'relay1',
                    'controller': {
                        'id': 1,
                        'name': 'kegboard'
                    },
                    'name': 'kegboard.relay1'
                },
            ],
            'meta': { 'result': 'ok'}
        }
        self.assertEquals(expected, data)

