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

from builtins import str
from django.core import mail
from django.urls import reverse
from django.test import TransactionTestCase
from django.test.utils import override_settings
from pykeg.core import models
from pykeg.core import defaults
from pykeg.core.testutils import get_filename
from pykeg.core.util import get_version
from pykeg.util import kbjson

# Helper methods


def create_site():
    return defaults.set_defaults(set_is_setup=True, create_controller=True)


class BaseApiTestCase(TransactionTestCase):
    def get(self, subpath, data={}, follow=False, **extra):
        response = self.client.get('/api/%s' % subpath, data=data, follow=follow,
                                   **extra)
        return response, kbjson.loads(response.content)

    def post(self, subpath, data={}, follow=False, **extra):
        response = self.client.post('/api/%s' % subpath, data=data, follow=follow,
                                    **extra)
        return response, kbjson.loads(response.content)

    def delete(self, subpath, data={}, follow=False, **extra):
        response = self.client.delete('/api/%s' % subpath, data=data, follow=follow,
                                      **extra)
        return response, kbjson.loads(response.content)


class ApiClientNoSiteTestCase(BaseApiTestCase):
    def testNotSetUp(self):
        '''Api endpoints should all error out prior to site setup.'''

        endpoints = ('events/', 'taps/', 'kegs/', 'drinks/')
        for endpoint in endpoints:
            response, data = self.get(endpoint)
            self.assertEqual(data.meta.result, 'error')
            self.assertEqual(data.error.code, 'BadRequestError')

        create_site()

        # Ordinary results expected after site installed.
        for endpoint in endpoints:
            response, data = self.get(endpoint)
            self.assertEqual(data.meta.result, 'ok')


@override_settings(KEGBOT_BACKEND='pykeg.core.testutils.TestBackend')
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

    def test_defaults(self):
        empty_endpoints = ('events/', 'kegs/')
        for endpoint in empty_endpoints:
            response, data = self.get(endpoint)
            self.assertEqual(data.objects, [])

        response, data = self.get('taps/')
        taps = data.objects
        self.assertEqual(2, len(taps))
        self.assertEqual('Main Tap', taps[0].name)
        self.assertEqual('kegboard.flow0', taps[0].meter_name)
        self.assertEqual('Second Tap', taps[1].name)
        self.assertEqual('kegboard.flow1', taps[1].meter_name)

        for tap in taps:
            response1, data1 = self.get('taps/%s' % tap.meter_name)
            self.assertEqual(data1.meta.result, 'ok')

            response2, data2 = self.get('taps/%s' % tap.id)
            self.assertEqual(data2.meta.result, 'ok')

            self.assertEqual(data1, data2)

    def test_api_access(self):
        endpoint = 'users/'

        # No API key.
        response, data = self.get(endpoint)
        self.assertEqual(data.meta.result, 'error')
        self.assertEqual(data.error.code, 'NoAuthTokenError')

        # Non-existent key.
        response, data = self.get(endpoint, HTTP_X_KEGBOT_API_KEY='foobar')
        self.assertEqual(data.meta.result, 'error')
        self.assertEqual(data.error.code, 'BadApiKeyError')

        # Key exists, non-superuser.
        response, data = self.get(endpoint, HTTP_X_KEGBOT_API_KEY=self.bad_apikey.key)
        self.assertEqual(data.meta.result, 'ok')

        # Finally ok.
        response, data = self.get(endpoint, HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEqual(data.meta.result, 'ok')

        endpoint = 'events/'

        # Alter privacy and compare.
        response, data = self.get(endpoint)
        self.assertEqual(data.meta.result, 'ok')
        self.site.privacy = 'members'
        self.site.save()

        response, data = self.get(endpoint)
        self.assertEqual(data.meta.result, 'error')

        self.client.login(username='admin', password='testpass')
        response, data = self.get(endpoint)
        self.assertEqual(data.meta.result, 'ok')

        # Alert to staff-only.
        self.site.privacy = 'staff'
        self.site.save()
        response, data = self.get(endpoint)
        self.assertEqual(data.meta.result, 'ok')

        self.client.logout()
        response, data = self.get(endpoint)
        self.assertEqual(data.meta.result, 'error')
        self.assertEqual(data.error.code, 'NoAuthTokenError')

        # Login endpoint works despite privacy settings
        for ep in ('login', 'login/', 'v1/login', 'v1/login/'):
            response, data = self.post(ep, data={'username': 'admin', 'password': 'testpass'})
            self.assertEqual(data.meta.result, 'ok')

        for ep in ('version/', 'v1/version/'):
            response, data = self.get(ep)
            self.assertEqual(data.meta.result, 'ok')

    def test_record_drink(self):
        response, data = self.get('taps/1')
        self.assertEqual(data.meta.result, 'ok')
        self.assertEqual(data.object.get('current_keg'), None)

        response, data = self.get('drinks/last')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data.meta.result, 'error')

        new_keg_data = {
            'keg_size': 'half-barrel',
            'beverage_name': 'Test Brew',
            'producer_name': 'Test Producer',
            'style_name': 'Test Style,'
        }
        response, data = self.post('taps/1/activate', data=new_keg_data)
        self.assertEqual(data.meta.result, 'error')
        self.assertEqual(data.error.code, 'NoAuthTokenError')

        response, data = self.post('taps/1/activate', data=new_keg_data,
                                   HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEqual(data.meta.result, 'ok')
        self.assertIsNotNone(data.object.get('current_keg'))

        response, data = self.post('taps/1', data={'ticks': 1000})
        self.assertEqual(data.meta.result, 'error')
        self.assertEqual(data.error.code, 'NoAuthTokenError')

        response, data = self.post('taps/1', HTTP_X_KEGBOT_API_KEY=self.apikey.key,
                                   data={'ticks': 1000, 'username': self.normal_user.username})
        self.assertEqual(data.meta.result, 'ok')
        drink = data.object

        response, data = self.get('drinks/last')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data.meta.result, 'ok')
        self.assertEqual(data.object.id, drink.id)

        response, data = self.get('status', HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEqual(data.meta.result, 'ok')
        users = data.object.get('active_users', [])
        self.assertEqual(1, len(users))
        active_user = users[0]
        self.assertEqual(self.normal_user.username, active_user.username)

    def test_record_drink_usernames(self):
        new_keg_data = {
            'keg_size': 'half-barrel',
            'beverage_name': 'Test Brew',
            'producer_name': 'Test Producer',
            'style_name': 'Test Style,'
        }
        response, data = self.post('taps/1/activate', data=new_keg_data,
                                   HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEqual(data.meta.result, 'ok')

        models.User.objects.create(username='test.123')
        response, data = self.post('taps/1', HTTP_X_KEGBOT_API_KEY=self.apikey.key,
            data={'ticks': 1000, 'username': 'test.123'})
        self.assertEqual(data.meta.result, 'ok')

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    @override_settings(EMAIL_FROM_ADDRESS='test-from@example')
    def test_registration(self):
        response, data = self.post(
            'new-user/', data={'username': 'newuser', 'email': 'foo@example.com'})
        self.assertEqual(data.meta.result, 'error')
        self.assertEqual(data.error.code, 'NoAuthTokenError')

        self.assertEqual(0, len(mail.outbox))

        response, data = self.post('new-user/', data={'username': 'newuser', 'email': 'foo@example.com'},
                                   HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEqual(data.meta.result, 'ok')
        self.assertEqual(1, len(mail.outbox))

        msg = mail.outbox[0]
        self.assertEqual('[My Kegbot] Complete your registration', msg.subject)
        self.assertEqual(['foo@example.com'], msg.to)
        self.assertEqual('test-from@example', msg.from_email)

        # Simulate clicking on the activation link.
        user = models.User.objects.get(username='newuser')
        self.assertIsNotNone(user.activation_key)
        activation_url = reverse('activate-account', args=(),
                                 kwargs={'activation_key': user.activation_key})
        self.client.logout()
        response = self.client.get(activation_url)
        self.assertContains(response, 'Choose a Password', status_code=200)

    def test_pictures(self):
        image_data = open(get_filename('test_image_800x600.png'), 'rb')
        response, data = self.post(
            'pictures/', data={'photo': image_data}, HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEqual(data.meta.result, 'ok')

        picture = data['object']
        picture_url = picture['url']
        self.assertTrue(picture_url.startswith('http://localhost:1234/media/'))

    def test_controller_data(self):
        for endpoint in ('controllers', 'flow-meters'):
            response, data = self.get(endpoint)
            self.assertEqual(data.meta.result, 'error')
            self.assertEqual(data.error.code, 'NoAuthTokenError')

        response, data = self.get('controllers', HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEqual(data.meta.result, 'ok')
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
        self.assertEqual(expected, data)

        response, data = self.get('flow-meters', HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEqual(data.meta.result, 'ok')
        expected = {
            'objects': [
                {
                    'id': 1,
                    'ticks_per_ml': 2.724,
                    'port_name': 'flow0',
                    'controller': {
                        'id': 1,
                        'name': 'kegboard',
                    },
                    'name': 'kegboard.flow0'
                },
                {
                    'id': 2,
                    'ticks_per_ml': 2.724,
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
        self.assertEqual(expected, data)

        response, data = self.get('flow-toggles', HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEqual(data.meta.result, 'ok')
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
        self.assertEqual(expected, data)

    def test_add_remove_meters(self):
        response, data = self.get('taps/1', HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEqual(data.meta.result, 'ok')
        self.assertEqual(data.object.meter.id, 1)
        original_data = data

        response, data = self.post('taps/1/disconnect-meter', HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEqual(data.meta.result, 'ok')
        self.assertEqual(data.object.get('meter'), None)

        response, data = self.post('taps/1/connect-meter', HTTP_X_KEGBOT_API_KEY=self.apikey.key,
                                   data={'meter': 1})
        self.assertEqual(data.meta.result, 'ok')
        self.assertEqual(data.object.meter.id, 1)
        self.assertEqual(original_data, data)

    def test_add_remove_toggles(self):
        response, data = self.get('taps/1', HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEqual(data.meta.result, 'ok')
        self.assertEqual(data.object.toggle.id, 1)

        response, data = self.post('taps/1/disconnect-toggle',
                                   HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEqual(data.meta.result, 'ok')
        self.assertEqual(data.object.get('toggle'), None)

        response, data = self.post('taps/1/connect-toggle', HTTP_X_KEGBOT_API_KEY=self.apikey.key,
                                   data={'toggle': 1})
        response, data = self.get('taps/1', HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEqual(data.meta.result, 'ok')
        self.assertIsNotNone(data.object.get('toggle'))
        self.assertEqual(data.object.toggle.id, 1)

    def test_get_version(self):
        response, data = self.get('version')
        self.assertEqual(data.meta.result, 'ok')
        self.assertEqual(data.object.get('server_version'), get_version())

    def test_devices(self):
        # Perform a device link.
        response, data = self.post('devices/link', data={'name': 'Test Device'})
        self.assertEqual(data.meta.result, 'ok')
        code = data.object.code

        response, data = self.get('devices/link/status/' + code)
        self.assertEqual(data.meta.result, 'ok')
        self.assertEqual(False, data.object.linked)

        self.client.login(username='admin', password='testpass')
        response = self.client.post('/kegadmin/devices/link/', data={'code': code}, follow=True)
        self.client.logout()
        self.assertEqual(response.status_code, 200)

        response, data = self.get('devices/link/status/' + code)
        self.assertEqual(data.meta.result, 'ok')
        self.assertEqual(True, data.object.linked)
        api_key = data.object.get('api_key')
        self.assertIsNotNone(api_key)

        key_obj = models.ApiKey.objects.get(key=api_key)
        self.assertIsNotNone(key_obj.device)
        self.assertEqual('Test Device', key_obj.device.name)

        # Confirm device key is gone.
        response, data = self.get('devices/link/status/' + code)
        self.assertEqual(response.status_code, 404)

    # Kegbot object tests

    def test_auth_tokens(self):
        response, data = self.get('auth-tokens/nfc/deadbeef', HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEqual(data.meta.result, 'error')
        self.assertEqual(response.status_code, 404)

        response, data = self.post(
            'auth-tokens/nfc/deadbeef/assign', HTTP_X_KEGBOT_API_KEY=self.apikey.key, data={
                'username': self.normal_user.username})
        self.assertEqual(data.meta.result, 'ok')
        self.assertEqual(data.object.auth_device, 'nfc')
        self.assertEqual(data.object.token_value, 'deadbeef')
        self.assertEqual(data.object.username, 'normal_user')
        self.assertEqual(response.status_code, 200)

    def test_controllers(self):
        """List, create, update, and delete controllers."""
        # List controllers.
        response, data = self.get('controllers', HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(1, len(data.objects))
        self.assertEqual('kegboard', data.objects[0]['name'])

        # Create a new controller.
        response, data = self.post('controllers', HTTP_X_KEGBOT_API_KEY=self.apikey.key,
                                   data={
                                       'name': 'Test Controller',
                                       'model_name': 'Test Model',
                                       'serial_number': 'Test Serial'
                                   })
        self.assertEqual(response.status_code, 200)
        self.assertEqual('Test Controller', data.object.name)
        self.assertEqual('Test Model', data.object.model_name)
        self.assertEqual('Test Serial', data.object.serial_number)

        # Fetch controller.
        new_controller_id = data.object.id
        response, data = self.get('controllers/' + str(new_controller_id),
                                  HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEqual(response.status_code, 200)
        self.assertEqual('Test Controller', data.object.name)
        self.assertEqual('Test Model', data.object.model_name)
        self.assertEqual('Test Serial', data.object.serial_number)

        # Update controller
        response, data = self.post(
            'controllers/' + str(new_controller_id), HTTP_X_KEGBOT_API_KEY=self.apikey.key, data={
                'name': 'Test Controller+', 'model_name': 'Test Model+', 'serial_number': 'Test Serial+'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual('Test Controller+', data.object.name)
        self.assertEqual('Test Model+', data.object.model_name)
        self.assertEqual('Test Serial+', data.object.serial_number)

        response, data = self.get('controllers/' + str(new_controller_id),
                                  HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEqual(response.status_code, 200)
        self.assertEqual('Test Controller+', data.object.name)
        self.assertEqual('Test Model+', data.object.model_name)
        self.assertEqual('Test Serial+', data.object.serial_number)

        # Delete controller
        response, data = self.delete('controllers/' + str(new_controller_id))
        self.assertEqual(response.status_code, 401)
        response, data = self.delete('controllers/' +
                                     str(new_controller_id), HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEqual(response.status_code, 200)
        response, data = self.get('controllers/' + str(new_controller_id),
                                  HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEqual(response.status_code, 404)

    def test_flow_meters(self):
        """List, create, update, and delete flow meters."""
        # List flow meters.
        response, data = self.get('flow-meters', HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(2, len(data.objects))
        self.assertEqual('kegboard.flow0', data.objects[0]['name'])
        self.assertEqual('flow0', data.objects[0]['port_name'])
        self.assertEqual('kegboard.flow1', data.objects[1]['name'])
        self.assertEqual('flow1', data.objects[1]['port_name'])

        # Create a new meter.
        controller = models.Controller.objects.all()[0]
        response, data = self.post('flow-meters', HTTP_X_KEGBOT_API_KEY=self.apikey.key,
                                   data={
                                       'port_name': 'flow-test',
                                       'ticks_per_ml': 3.45,
                                       'controller': controller.id,
                                   })
        self.assertEqual(response.status_code, 200)
        self.assertEqual('kegboard.flow-test', data.object.name)
        self.assertEqual('flow-test', data.object.port_name)
        self.assertEqual(3.45, data.object.ticks_per_ml)
        self.assertEqual(controller.name, data.object.controller.name)

        # Fetch meter.
        new_meter_id = data.object.id
        response, data = self.get('flow-meters/' + str(new_meter_id),
                                  HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEqual(response.status_code, 200)
        self.assertEqual('kegboard.flow-test', data.object.name)
        self.assertEqual('flow-test', data.object.port_name)
        self.assertEqual(3.45, data.object.ticks_per_ml)
        self.assertEqual(controller.name, data.object.controller.name)

        # Update meter
        response, data = self.post('flow-meters/' + str(new_meter_id),
                                   HTTP_X_KEGBOT_API_KEY=self.apikey.key, data={'ticks_per_ml': 5.67, })
        self.assertEqual(response.status_code, 200)
        self.assertEqual('kegboard.flow-test', data.object.name)
        self.assertEqual(5.67, data.object.ticks_per_ml)
        self.assertEqual(controller.name, data.object.controller.name)

        # Delete meter
        response, data = self.delete('flow-meters/' + str(new_meter_id))
        self.assertEqual(response.status_code, 401)
        response, data = self.delete('flow-meters/' + str(new_meter_id),
                                     HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEqual(response.status_code, 200)
        response, data = self.get('flow-meters/' + str(new_meter_id),
                                  HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEqual(response.status_code, 404)

    def test_flow_toggles(self):
        """List, create, and delete flow toggles."""
        # List flow toggles.
        response, data = self.get('flow-toggles', HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(2, len(data.objects))
        self.assertEqual('kegboard.relay0', data.objects[0]['name'])
        self.assertEqual('relay0', data.objects[0]['port_name'])
        self.assertEqual('kegboard.relay1', data.objects[1]['name'])
        self.assertEqual('relay1', data.objects[1]['port_name'])

        # Create a new toggle.
        controller = models.Controller.objects.all()[0]
        response, data = self.post('flow-toggles', HTTP_X_KEGBOT_API_KEY=self.apikey.key,
                                   data={
                                       'port_name': 'toggle-test',
                                       'controller': controller.id,
                                   })
        self.assertEqual(response.status_code, 200)
        self.assertEqual('kegboard.toggle-test', data.object.name)
        self.assertEqual('toggle-test', data.object.port_name)
        self.assertEqual(controller.name, data.object.controller.name)

        # Fetch toggle.
        new_toggle_id = data.object.id
        response, data = self.get('flow-toggles/' + str(new_toggle_id),
                                  HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEqual(response.status_code, 200)
        self.assertEqual('kegboard.toggle-test', data.object.name)
        self.assertEqual('toggle-test', data.object.port_name)
        self.assertEqual(controller.name, data.object.controller.name)

        # Delete toggle.
        response, data = self.delete('flow-toggles/' + str(new_toggle_id))
        self.assertEqual(response.status_code, 401)
        response, data = self.delete('flow-toggles/' +
                                     str(new_toggle_id), HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEqual(response.status_code, 200)
        response, data = self.get('flow-toggles/' + str(new_toggle_id),
                                  HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEqual(response.status_code, 404)

    def test_taps(self):
        """List, create, and delete taps."""
        # List flow toggles.
        response, data = self.get('taps', HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(2, len(data.objects))
        self.assertEqual('Main Tap', data.objects[0]['name'])
        self.assertEqual('Second Tap', data.objects[1]['name'])

        # Create a new toggle.
        response, data = self.post('taps', HTTP_X_KEGBOT_API_KEY=self.apikey.key,
                                   data={
                                       'name': 'Test Tap',
                                   })
        self.assertEqual(response.status_code, 200)
        self.assertEqual('Test Tap', data.object.name)

        # Fetch tap.
        tap_id = data.object.id
        response, data = self.get('taps/' + str(tap_id), HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEqual(response.status_code, 200)
        self.assertEqual('Test Tap', data.object.name)

        # Delete tap.
        response, data = self.delete('taps/' + str(tap_id))
        self.assertEqual(response.status_code, 401)
        response, data = self.delete('taps/' + str(tap_id), HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEqual(response.status_code, 200)
        response, data = self.get('taps/' + str(tap_id), HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEqual(response.status_code, 404)
