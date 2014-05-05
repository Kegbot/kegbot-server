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

from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TransactionTestCase
from django.test.utils import override_settings
from pykeg.core import models
from pykeg.core import defaults
from pykeg.core.util import get_version
from kegbot.util import kbjson

import os
TESTDATA_DIR = os.path.join(os.path.dirname(__file__), 'testdata/')

### Helper methods


def create_site():
    return defaults.set_defaults(set_is_setup=True, create_controller=True)


def get_filename(f):
    return os.path.join(TESTDATA_DIR, f)


class BaseApiTestCase(TransactionTestCase):
    def get(self, subpath, data={}, follow=False, **extra):
        response = self.client.get('/api/%s' % subpath, data=data, follow=follow,
            **extra)
        return response, kbjson.loads(response.content)

    def post(self, subpath, data={}, follow=False, **extra):
        response = self.client.post('/api/%s' % subpath, data=data, follow=follow,
            **extra)
        return response, kbjson.loads(response.content)


class ApiClientNoSiteTestCase(BaseApiTestCase):
    def testNotSetUp(self):
        '''Api endpoints should all error out prior to site setup.'''

        endpoints = ('events/', 'taps/', 'kegs/', 'drinks/')
        for endpoint in endpoints:
            response, data = self.get(endpoint)
            self.assertEquals(data.meta.result, 'error')
            self.assertEquals(data.error.code, 'BadRequestError')

        create_site()

        # Ordinary results expected after site installed.
        for endpoint in endpoints:
            response, data = self.get(endpoint)
            self.assertEquals(data.meta.result, 'ok')


class ApiClientTestCase(BaseApiTestCase):
    def setUp(self):
        self.site = create_site()
        self.admin = models.User.objects.create(username='admin', is_staff=True)
        self.admin.set_password('testpass')
        self.admin.save()

        self.normal_user = models.User.objects.create(username='normal_user', is_staff=True)
        self.normal_user.set_password('testpass')
        self.normal_user.save()

        self.apikey = models.ApiKey.objects.create(user=self.admin, key='123')
        self.bad_apikey = models.ApiKey.objects.create(user=self.normal_user, key='456')

    def testSiteDefaults(self):
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
        endpoint = 'users/'

        # No API key.
        response, data = self.get(endpoint)
        self.assertEquals(data.meta.result, 'error')
        self.assertEquals(data.error.code, 'NoAuthTokenError')

        # Non-existent key.
        response, data = self.get(endpoint, HTTP_X_KEGBOT_API_KEY='foobar')
        self.assertEquals(data.meta.result, 'error')
        self.assertEquals(data.error.code, 'BadApiKeyError')

        # Key exists, non-superuser.
        response, data = self.get(endpoint, HTTP_X_KEGBOT_API_KEY=self.bad_apikey.key)
        self.assertEquals(data.meta.result, 'ok')

        # Finally ok.
        response, data = self.get(endpoint, HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEquals(data.meta.result, 'ok')

        endpoint = 'events/'

        # Alter privacy and compare.
        response, data = self.get(endpoint)
        self.assertEquals(data.meta.result, 'ok')
        self.site.privacy = 'members'
        self.site.save()

        response, data = self.get(endpoint)
        self.assertEquals(data.meta.result, 'error')

        self.client.login(username='admin', password='testpass')
        response, data = self.get(endpoint)
        self.assertEquals(data.meta.result, 'ok')

        # Alert to staff-only.
        self.site.privacy = 'staff'
        self.site.save()
        response, data = self.get(endpoint)
        self.assertEquals(data.meta.result, 'ok')

        self.client.logout()
        response, data = self.get(endpoint)
        self.assertEquals(data.meta.result, 'error')
        self.assertEquals(data.error.code, 'NoAuthTokenError')

        # Login endpoint works despite privacy settings
        for ep in ('login', 'login/', 'v1/login', 'v1/login/'):
            response, data = self.post(ep, data={'username': 'admin', 'password': 'testpass'})
            self.assertEquals(data.meta.result, 'ok')

        for ep in ('version/', 'v1/version/'):
            response, data = self.get(ep)
            self.assertEquals(data.meta.result, 'ok')

    def test_record_drink(self):
        response, data = self.get('taps/1')
        self.assertEquals(data.meta.result, 'ok')
        self.assertEquals(data.object.get('current_keg'), None)

        new_keg_data = {
            'keg_size': 'half-barrel',
            'beverage_name': 'Test Brew',
            'producer_name': 'Test Producer',
            'style_name': 'Test Style,'
        }
        response, data = self.post('taps/1/activate', data=new_keg_data)
        self.assertEquals(data.meta.result, 'error')
        self.assertEquals(data.error.code, 'NoAuthTokenError')

        response, data = self.post('taps/1/activate', data=new_keg_data,
            HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEquals(data.meta.result, 'ok')
        self.assertIsNotNone(data.object.get('current_keg'))

        response, data = self.post('taps/1', data={'ticks': 1000})
        self.assertEquals(data.meta.result, 'error')
        self.assertEquals(data.error.code, 'NoAuthTokenError')

        response, data = self.post('taps/1', HTTP_X_KEGBOT_API_KEY=self.apikey.key,
            data={'ticks': 1000})
        self.assertEquals(data.meta.result, 'ok')

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    @override_settings(EMAIL_FROM_ADDRESS='test-from@example')
    def test_registration(self):
        response, data = self.post('new-user/', data={'username': 'newuser', 'email': 'foo@example.com'})
        self.assertEquals(data.meta.result, 'error')
        self.assertEquals(data.error.code, 'NoAuthTokenError')

        self.assertEquals(0, len(mail.outbox))

        response, data = self.post('new-user/', data={'username': 'newuser', 'email': 'foo@example.com'},
            HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEquals(data.meta.result, 'ok')
        self.assertEquals(1, len(mail.outbox))

        msg = mail.outbox[0]
        self.assertEquals('[My Kegbot] Complete your registration', msg.subject)
        self.assertEquals(['foo@example.com'], msg.to)
        self.assertEquals('test-from@example', msg.from_email)

        # Simulate clicking on the activation link.
        user = models.User.objects.get(username='newuser')
        self.assertIsNotNone(user.activation_key)
        activation_url = reverse('activate-account', args=(),
            kwargs={'activation_key': user.activation_key})
        self.client.logout()
        response = self.client.get(activation_url)
        self.assertContains(response, 'Choose a Password', status_code=200)

    def test_pictures(self):
        kbsite = models.KegbotSite.get()
        kbsite.hostname = 'localhost:123'
        kbsite.use_ssl = True
        kbsite.save()

        image_data = open(get_filename('test_image_800x600.png'))
        response, data = self.post('pictures/', data={'photo': image_data}, HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        print data
        self.assertEquals(data.meta.result, 'ok')

        picture = data['object']
        picture_url = picture['url']
        self.assertTrue(picture_url.startswith('https://localhost:123/media/'))

    def test_controller_data(self):
        for endpoint in ('controllers', 'flow-meters'):
            response, data = self.get(endpoint)
            self.assertEquals(data.meta.result, 'error')
            self.assertEquals(data.error.code, 'NoAuthTokenError')

        response, data = self.get('controllers', HTTP_X_KEGBOT_API_KEY=self.apikey.key)
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

        response, data = self.get('flow-meters', HTTP_X_KEGBOT_API_KEY=self.apikey.key)
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
            'meta': {'result': 'ok'}
        }
        self.assertEquals(expected, data)

        response, data = self.get('flow-toggles', HTTP_X_KEGBOT_API_KEY=self.apikey.key)
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
            'meta': {'result': 'ok'}
        }
        self.assertEquals(expected, data)

    def test_add_remove_meters(self):
        response, data = self.get('taps/1', HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEquals(data.meta.result, 'ok')
        self.assertEquals(data.object.meter.id, 1)
        original_data = data

        response, data = self.post('taps/1/disconnect-meter', HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEquals(data.meta.result, 'ok')
        self.assertEquals(data.object.get('meter'), None)

        response, data = self.post('taps/1/connect-meter', HTTP_X_KEGBOT_API_KEY=self.apikey.key,
            data={'meter': 1})
        self.assertEquals(data.meta.result, 'ok')
        self.assertEquals(data.object.meter.id, 1)
        self.assertEquals(original_data, data)

    def test_add_remove_toggles(self):
        response, data = self.get('taps/1', HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEquals(data.meta.result, 'ok')
        self.assertEquals(data.object.toggle.id, 1)

        response, data = self.post('taps/1/disconnect-toggle', HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEquals(data.meta.result, 'ok')
        self.assertEquals(data.object.get('toggle'), None)

        response, data = self.post('taps/1/connect-toggle', HTTP_X_KEGBOT_API_KEY=self.apikey.key,
            data={'toggle': 1})
        response, data = self.get('taps/1', HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEquals(data.meta.result, 'ok')
        self.assertIsNotNone(data.object.get('toggle'))
        self.assertEquals(data.object.toggle.id, 1)

    def test_get_version(self):
        response, data = self.get('version')
        self.assertEquals(data.meta.result, 'ok')
        self.assertEquals(data.object.get('server_version'), get_version())

    def test_auth_tokens(self):
        response, data = self.get('auth-tokens/nfc/deadbeef', HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEquals(data.meta.result, 'error')
        self.assertEquals(response.status_code, 404)

        response, data = self.post('auth-tokens/nfc/deadbeef/assign', HTTP_X_KEGBOT_API_KEY=self.apikey.key,
            data={'username': self.normal_user.username})
        self.assertEquals(data.meta.result, 'ok')
        self.assertEquals(data.object.auth_device, 'nfc')
        self.assertEquals(data.object.token_value, 'deadbeef')
        self.assertEquals(data.object.username, 'normal_user')
        self.assertEquals(response.status_code, 200)
