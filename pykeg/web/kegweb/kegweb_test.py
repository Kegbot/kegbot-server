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

"""General tests for the web interface."""

from django.core import mail
from django.test import TransactionTestCase
from django.test.utils import override_settings
from django.core.urlresolvers import reverse

from pykeg.backend import get_kegbot_backend
from pykeg.core import models
from pykeg.core import defaults


@override_settings(KEGBOT_BACKEND='pykeg.core.testutils.TestBackend')
class KegwebTestCase(TransactionTestCase):
    def setUp(self):
        self.client.logout()
        defaults.set_defaults(set_is_setup=True, create_controller=True)

    def testBasicEndpoints(self):
        for endpoint in ('/kegs/', '/stats/', '/drinkers/guest/', '/drinkers/guest/sessions/'):
            response = self.client.get(endpoint)
            self.assertEquals(200, response.status_code)

        for endpoint in ('/sessions/',):
            response = self.client.get(endpoint)
            self.assertEquals(404, response.status_code)

        b = get_kegbot_backend()
        keg = b.start_keg('kegboard.flow0', beverage_name='Unknown', producer_name='Unknown',
            beverage_type='beer', style_name='Unknown')
        self.assertIsNotNone(keg)
        response = self.client.get('/kegs/')
        self.assertEquals(200, response.status_code)

        d = b.record_drink('kegboard.flow0', ticks=100)
        drink_id = d.id

        response = self.client.get('/d/%s' % drink_id, follow=True)
        self.assertRedirects(response, '/drinks/%s' % drink_id, status_code=301)

        session_id = d.session.id
        response = self.client.get('/s/%s' % session_id, follow=True)
        self.assertRedirects(response, d.session.get_absolute_url(), status_code=301)

    def testShout(self):
        b = get_kegbot_backend()
        b.start_keg('kegboard.flow0', beverage_name='Unknown', producer_name='Unknown',
            beverage_type='beer', style_name='Unknown')
        d = b.record_drink('kegboard.flow0', ticks=123, shout='_UNITTEST_')
        response = self.client.get(d.get_absolute_url())
        self.assertContains(response, '<p>_UNITTEST_</p>', status_code=200)

    def test_privacy(self):
        b = get_kegbot_backend()
        keg = b.start_keg('kegboard.flow0', beverage_name='Unknown', producer_name='Unknown',
            beverage_type='beer', style_name='Unknown')
        self.assertIsNotNone(keg)
        d = b.record_drink('kegboard.flow0', ticks=100)

        # URLs to expected contents
        urls = {
            '/kegs/': 'Keg List',
            '/stats/': 'System Stats',
            '/sessions/': 'All Sessions',
            '/kegs/{}'.format(keg.id): 'Keg {}'.format(keg.id),
            '/drinks/{}'.format(d.id): 'Drink {}'.format(d.id),
        }

        def test_urls(expect_fail, urls=urls):
            for url, expected_content in urls.iteritems():
                response = self.client.get(url)
                if expect_fail:
                    self.assertNotContains(response, expected_content, status_code=401,
                            msg_prefix=url)
                else:
                    self.assertContains(response, expected_content, status_code=200,
                            msg_prefix=url)

        b = get_kegbot_backend()
        user = b.create_new_user('testuser', 'test@example.com', password='1234')

        kbsite = models.KegbotSite.get()
        self.client.logout()

        # Public mode.
        test_urls(expect_fail=False)

        # Members-only.
        kbsite.privacy = 'members'
        kbsite.save()
        test_urls(expect_fail=True)
        logged_in = self.client.login(username='testuser', password='1234')
        self.assertTrue(logged_in)
        test_urls(expect_fail=False)

        # Staff-only
        kbsite.privacy = 'staff'
        kbsite.save()

        test_urls(expect_fail=True)
        user.is_staff = True
        user.save()
        test_urls(expect_fail=False)
        self.client.logout()
        test_urls(expect_fail=True)

    def test_whitelisted_urls(self):
        """Verify always-accessible URLs."""
        urls = (
            '/accounts/password/reset/',
            '/accounts/register/',
            '/accounts/login/',
        )

        for url in urls:
            response = self.client.get(url)
            self.assertNotContains(response, 'denied', status_code=200,
                    msg_prefix=url)

    def test_activation(self):
        b = get_kegbot_backend()
        kbsite = models.KegbotSite.get()
        self.assertEqual('public', kbsite.privacy)

        user = b.create_new_user('testuser', 'test@example.com')
        self.assertIsNotNone(user.activation_key)
        self.assertFalse(user.has_usable_password())

        activation_key = user.activation_key
        self.assertIsNotNone(activation_key)

        activation_url = reverse('activate-account', args=(),
            kwargs={'activation_key': activation_key})

        # Activation works regardless of privacy settings.
        self.client.logout()
        response = self.client.get(activation_url)
        self.assertContains(response, 'Choose a Password', status_code=200)

        kbsite.privacy = 'staff'
        kbsite.save()
        response = self.client.get(activation_url)
        self.assertContains(response, 'Choose a Password', status_code=200)

        kbsite.privacy = 'members'
        kbsite.save()
        response = self.client.get(activation_url)
        self.assertContains(response, 'Choose a Password', status_code=200)

        # Activate the account.
        form_data = {
            'password': '123',
            'password2': '123',
        }

        response = self.client.post(activation_url, data=form_data, follow=True)
        self.assertContains(response, 'Your account has been activated!', status_code=200)
        user = models.User.objects.get(pk=user.id)
        self.assertIsNone(user.activation_key)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    @override_settings(EMAIL_FROM_ADDRESS='test-from@example')
    def test_registration(self):
        kbsite = models.KegbotSite.get()
        self.assertEqual('public', kbsite.privacy)
        self.assertEqual('public', kbsite.registration_mode)

        response = self.client.get('/accounts/register/')
        self.assertContains(response, 'Register New Account', status_code=200)

        response = self.client.post('/accounts/register/',
            data={
                'username': 'newuser',
                'password1': '1234',
                'password2': '1234',
                'email': 'test2@example.com',
            }, follow=True)
        self.assertRedirects(response, '/account/')
        self.assertContains(response, 'Hello, newuser')
        self.assertEqual(1, len(mail.outbox))

        msg = mail.outbox[0]
        self.assertEqual(['test2@example.com'], msg.to)
        self.assertTrue('To log in to your account, please click here' in msg.body)

        response = self.client.post('/accounts/register/',
            data={
                'username': 'newuser',
                'password1': '1234',
                'password2': '1234',
                'email': 'test2@example.com',
            }, follow=False)
        self.assertContains(response, 'User with this Username already exists',
            status_code=200)

        response = self.client.post('/accounts/register/',
            data={
                'username': 'newuser 2',
                'password1': '1234',
                'password2': '1234',
                'email': 'test2@example.com',
            }, follow=False)
        self.assertContains(response, 'Enter a valid username',
            status_code=200)

        response = self.client.post('/accounts/register/',
            data={
                'username': 'newuser2',
                'password1': '1234',
                'password2': '1235',
                'email': 'test2@example.com',
            }, follow=False)
        print response
        self.assertContains(response, "The two password fields didn&#39;t match.",
            status_code=200)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    @override_settings(EMAIL_FROM_ADDRESS='test-from@example')
    def test_registration_with_invite(self):
        kbsite = models.KegbotSite.get()
        kbsite.registration_mode = 'staff-invite-online'
        kbsite.save()

        response = self.client.get('/accounts/register/')
        self.assertContains(response, 'Invitation Required', status_code=401)

        response = self.client.get('/accounts/register/?invite_code=1234')
        self.assertContains(response, 'Invitation Expired', status_code=401)

        models.Invitation.objects.create(invite_code='test', for_email='test@example.com')
        self.assertEqual(1, models.Invitation.objects.all().count())

        response = self.client.get('/accounts/register/?invite_code=test')
        self.assertContains(response, 'Register New Account', status_code=200)
        response = self.client.post('/accounts/register/',
            data={
                'username': 'newuser2',
                'password1': '1234',
                'password2': '1234',
                'email': 'test2@example.com',
            }, follow=True)
        self.assertRedirects(response, '/account/')
        self.assertContains(response, 'Hello, newuser2')
        self.assertEqual(0, models.Invitation.objects.all().count())

        response = self.client.get('/accounts/register/?invite_code=test')
        self.assertContains(response, 'Invitation Expired', status_code=401)

    def test_upgrade_bouncer(self):
        kbsite = models.KegbotSite.get()
        response = self.client.get('/')
        self.assertContains(response, 'My Kegbot', status_code=200)

        old_version = kbsite.server_version
        kbsite.server_version = '0.0.1'
        kbsite.save()
        response = self.client.get('/')
        self.assertContains(response, 'Upgrade Required', status_code=403)

        kbsite.server_version = old_version
        kbsite.is_setup = False
        kbsite.save()
        response = self.client.get('/')
        self.assertContains(response, 'Kegbot Offline', status_code=403)
