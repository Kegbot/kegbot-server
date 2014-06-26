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
from pykeg.core.testutils import get_filename
from pykeg.core.util import get_version
from kegbot.util import kbjson

### Helper methods


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
            self.assertEquals(data.meta.result, 'error')
            self.assertEquals(data.error.code, 'BadRequestError')

        create_site()

        # Ordinary results expected after site installed.
        for endpoint in endpoints:
            response, data = self.get(endpoint)
            self.assertEquals(data.meta.result, 'ok')


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

    def test_api_access(self):
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
            data={'ticks': 1000, 'username': self.normal_user.username})
        self.assertEquals(data.meta.result, 'ok')

        response, data = self.get('status', HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEquals(data.meta.result, 'ok')
        users = data.object.get('active_users', [])
        self.assertEquals(1, len(users))
        active_user = users[0]
        self.assertEquals(self.normal_user.username, active_user.username)

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
        image_data = open(get_filename('test_image_800x600.png'))
        response, data = self.post('pictures/', data={'photo': image_data}, HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEquals(data.meta.result, 'ok')

        picture = data['object']
        picture_url = picture['url']
        self.assertTrue(picture_url.startswith('http://localhost:1234/media/'))

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

    def test_devices(self):
        ### Perform a device link.
        response, data = self.post('devices/link', data={'name': 'Test Device'})
        self.assertEquals(data.meta.result, 'ok')
        code = data.object.code

        response, data = self.get('devices/link/status/' + code)
        self.assertEquals(data.meta.result, 'ok')
        self.assertEquals(False, data.object.linked)

        self.client.login(username='admin', password='testpass')
        response = self.client.post('/kegadmin/devices/link/', data={'code': code}, follow=True)
        self.client.logout()
        self.assertEquals(response.status_code, 200)

        response, data = self.get('devices/link/status/' + code)
        self.assertEquals(data.meta.result, 'ok')
        self.assertEquals(True, data.object.linked)
        api_key = data.object.get('api_key')
        self.assertIsNotNone(api_key)

        key_obj = models.ApiKey.objects.get(key=api_key)
        self.assertIsNotNone(key_obj.device)
        self.assertEquals('Test Device', key_obj.device.name)

        ### Confirm device key is gone.
        response, data = self.get('devices/link/status/' + code)
        self.assertEquals(response.status_code, 404)

    ### Kegbot object tests

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

    def test_controllers(self):
        """List, create, update, and delete controllers."""
        # List controllers.
        response, data = self.get('controllers', HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(1, len(data.objects))
        self.assertEquals('kegboard', data.objects[0]['name'])

        # Create a new controller.
        response, data = self.post('controllers', HTTP_X_KEGBOT_API_KEY=self.apikey.key,
            data={
                'name': 'Test Controller',
                'model_name': 'Test Model',
                'serial_number': 'Test Serial'
            })
        self.assertEquals(response.status_code, 200)
        self.assertEquals('Test Controller', data.object.name)
        self.assertEquals('Test Model', data.object.model_name)
        self.assertEquals('Test Serial', data.object.serial_number)

        # Fetch controller.
        new_controller_id = data.object.id
        response, data = self.get('controllers/' + str(new_controller_id), HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEquals(response.status_code, 200)
        self.assertEquals('Test Controller', data.object.name)
        self.assertEquals('Test Model', data.object.model_name)
        self.assertEquals('Test Serial', data.object.serial_number)

        # Update controller
        response, data = self.post('controllers/' + str(new_controller_id), HTTP_X_KEGBOT_API_KEY=self.apikey.key,
            data={
                'name': 'Test Controller+',
                'model_name': 'Test Model+',
                'serial_number': 'Test Serial+'})
        self.assertEquals(response.status_code, 200)
        self.assertEquals('Test Controller+', data.object.name)
        self.assertEquals('Test Model+', data.object.model_name)
        self.assertEquals('Test Serial+', data.object.serial_number)

        response, data = self.get('controllers/' + str(new_controller_id), HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEquals(response.status_code, 200)
        self.assertEquals('Test Controller+', data.object.name)
        self.assertEquals('Test Model+', data.object.model_name)
        self.assertEquals('Test Serial+', data.object.serial_number)

        # Delete controller
        response, data = self.delete('controllers/' + str(new_controller_id))
        self.assertEquals(response.status_code, 401)
        response, data = self.delete('controllers/' + str(new_controller_id), HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEquals(response.status_code, 200)
        response, data = self.get('controllers/' + str(new_controller_id), HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEquals(response.status_code, 404)

    def test_flow_meters(self):
        """List, create, update, and delete flow meters."""
        # List flow meters.
        response, data = self.get('flow-meters', HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(2, len(data.objects))
        self.assertEquals('kegboard.flow0', data.objects[0]['name'])
        self.assertEquals('flow0', data.objects[0]['port_name'])
        self.assertEquals('kegboard.flow1', data.objects[1]['name'])
        self.assertEquals('flow1', data.objects[1]['port_name'])

        # Create a new meter.
        controller = models.Controller.objects.all()[0]
        response, data = self.post('flow-meters', HTTP_X_KEGBOT_API_KEY=self.apikey.key,
            data={
                'port_name': 'flow-test',
                'ticks_per_ml': 3.45,
                'controller': controller.id,
            })
        self.assertEquals(response.status_code, 200)
        self.assertEquals('kegboard.flow-test', data.object.name)
        self.assertEquals('flow-test', data.object.port_name)
        self.assertEquals(3.45, data.object.ticks_per_ml)
        self.assertEquals(controller.name, data.object.controller.name)

        # Fetch meter.
        new_meter_id = data.object.id
        response, data = self.get('flow-meters/' + str(new_meter_id), HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEquals(response.status_code, 200)
        self.assertEquals('kegboard.flow-test', data.object.name)
        self.assertEquals('flow-test', data.object.port_name)
        self.assertEquals(3.45, data.object.ticks_per_ml)
        self.assertEquals(controller.name, data.object.controller.name)

        # Update meter
        response, data = self.post('flow-meters/' + str(new_meter_id), HTTP_X_KEGBOT_API_KEY=self.apikey.key,
        data={
            'ticks_per_ml': 5.67,
        })
        self.assertEquals(response.status_code, 200)
        self.assertEquals('kegboard.flow-test', data.object.name)
        self.assertEquals(5.67, data.object.ticks_per_ml)
        self.assertEquals(controller.name, data.object.controller.name)

        # Delete meter
        response, data = self.delete('flow-meters/' + str(new_meter_id))
        self.assertEquals(response.status_code, 401)
        response, data = self.delete('flow-meters/' + str(new_meter_id), HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEquals(response.status_code, 200)
        response, data = self.get('flow-meters/' + str(new_meter_id), HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEquals(response.status_code, 404)

    def test_flow_toggles(self):
        """List, create, and delete flow toggles."""
        # List flow toggles.
        response, data = self.get('flow-toggles', HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(2, len(data.objects))
        self.assertEquals('kegboard.relay0', data.objects[0]['name'])
        self.assertEquals('relay0', data.objects[0]['port_name'])
        self.assertEquals('kegboard.relay1', data.objects[1]['name'])
        self.assertEquals('relay1', data.objects[1]['port_name'])

        # Create a new toggle.
        controller = models.Controller.objects.all()[0]
        response, data = self.post('flow-toggles', HTTP_X_KEGBOT_API_KEY=self.apikey.key,
            data={
                'port_name': 'toggle-test',
                'controller': controller.id,
            })
        self.assertEquals(response.status_code, 200)
        self.assertEquals('kegboard.toggle-test', data.object.name)
        self.assertEquals('toggle-test', data.object.port_name)
        self.assertEquals(controller.name, data.object.controller.name)

        # Fetch toggle.
        new_toggle_id = data.object.id
        response, data = self.get('flow-toggles/' + str(new_toggle_id), HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEquals(response.status_code, 200)
        self.assertEquals('kegboard.toggle-test', data.object.name)
        self.assertEquals('toggle-test', data.object.port_name)
        self.assertEquals(controller.name, data.object.controller.name)

        # Delete toggle.
        response, data = self.delete('flow-toggles/' + str(new_toggle_id))
        self.assertEquals(response.status_code, 401)
        response, data = self.delete('flow-toggles/' + str(new_toggle_id), HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEquals(response.status_code, 200)
        response, data = self.get('flow-toggles/' + str(new_toggle_id), HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEquals(response.status_code, 404)

    def test_taps(self):
        """List, create, and delete taps."""
        # List flow toggles.
        response, data = self.get('taps', HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(2, len(data.objects))
        self.assertEquals('Main Tap', data.objects[0]['name'])
        self.assertEquals('Second Tap', data.objects[1]['name'])

        # Create a new toggle.
        response, data = self.post('taps', HTTP_X_KEGBOT_API_KEY=self.apikey.key,
            data={
                'name': 'Test Tap',
            })
        self.assertEquals(response.status_code, 200)
        self.assertEquals('Test Tap', data.object.name)

        # Fetch tap.
        tap_id = data.object.id
        response, data = self.get('taps/' + str(tap_id), HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEquals(response.status_code, 200)
        self.assertEquals('Test Tap', data.object.name)

        # Delete tap.
        response, data = self.delete('taps/' + str(tap_id))
        self.assertEquals(response.status_code, 401)
        response, data = self.delete('taps/' + str(tap_id), HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEquals(response.status_code, 200)
        response, data = self.get('taps/' + str(tap_id), HTTP_X_KEGBOT_API_KEY=self.apikey.key)
        self.assertEquals(response.status_code, 404)
