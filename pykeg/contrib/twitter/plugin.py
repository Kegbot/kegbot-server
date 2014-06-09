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

"""Twitter plugin for Kegbot."""

from django.conf import settings
from pykeg.plugin import plugin
from pykeg.plugin import util

from pykeg.core.models import KegbotSite
from pykeg.core.util import SuppressTaskErrors
from socialregistration.contrib.twitter.client import Twitter
import oauth2 as oauth

from . import forms
from . import tasks
from . import views

from unicodedata import normalize

KEY_CONSUMER_KEY = 'consumer_key'
KEY_CONSUMER_SECRET = 'consumer_secret'

KEY_SITE_PROFILE = 'site_profile'
KEY_OAUTH_TOKEN = 'oauth_token'
KEY_OAUTH_TOKEN_SECRET = 'oauth_token_secret'
KEY_TWITTER_NAME = 'twitter_name'
KEY_TWITTER_ID = 'twitter_id'

KEY_SITE_SETTINGS = 'site_settings'

TWITTER_LINK_LEN = 22
TWEET_MAX_LEN = 140
TWEET_MAX_LEN_WITH_URL = TWEET_MAX_LEN - TWITTER_LINK_LEN - 1
TRUNCATE_STR = u'\u2026'


def send_tweet(api, contents):
    """Sends a tweet using `api`."""
    return api.update_status(contents)


def truncate_tweet(tweet, max_len=TWEET_MAX_LEN, truncate_str=TRUNCATE_STR):
    if len(tweet) <= max_len:
        return tweet
    words = tweet.strip().split()
    while True:
        tweet = u' '.join(words)
        candidate = normalize('NFC', tweet + truncate_str)
        if not tweet or len(candidate) <= max_len:
            return candidate
        words = words[:-1]


class TwitterClient(Twitter):
    def set_callback_url(self, url):
        self.callback_url = url

    def get_callback_url(self):
        return self.callback_url


class TwitterPlugin(plugin.Plugin):
    NAME = 'Twitter'
    SHORT_NAME = 'twitter'
    DESCRIPTION = 'Tweet when you pour!'
    URL = 'http://kegbot.org'
    VERSION = '0.0.1-pre'

    def get_admin_settings_view(self):
        return views.admin_settings

    def get_user_settings_view(self):
        return views.user_settings

    def get_extra_admin_views(self):
        return [
            ('redirect/$', 'pykeg.contrib.twitter.views.site_twitter_redirect', 'site_twitter_redirect'),
            ('callback/$', 'pykeg.contrib.twitter.views.site_twitter_callback', 'site_twitter_callback'),
        ]

    def get_extra_user_views(self):
        return [
            ('redirect/$', 'pykeg.contrib.twitter.views.user_twitter_redirect', 'user_twitter_redirect'),
            ('callback/$', 'pykeg.contrib.twitter.views.user_twitter_callback', 'user_twitter_callback'),
        ]

    def get_site_twitter_settings_form(self):
        return self.datastore.load_form(forms.SiteSettingsForm, KEY_SITE_SETTINGS)

    def handle_new_events(self, events):
        for event in events:
            self.handle_event(event)

    def handle_event(self, event):
        self.logger.info('Handling new event: %s' % event.id)
        if util.is_stale(event.time):
            self.logger.info('Event is stale, ignoring: %s' % event.id)
            return

        profile = self.get_site_profile()
        if not profile:
            self.logger.info('No site twitter profile, ignoring.')
            return

        site_settings = self.get_site_twitter_settings_form().initial

        self._issue_system_tweet(event, site_settings, profile)
        if event.user and not event.user.is_guest():
            self._issue_user_tweet(event, site_settings)

    ### Twitter-specific methods

    def get_site_profile(self):
        return self._get_profile(KEY_SITE_PROFILE)

    def get_user_profile(self, user):
        return self._get_profile('user_profile:%s' % user.id)

    def _get_profile(self, datastore_key):
        return self.datastore.get(datastore_key, {})

    def save_site_profile(self, oauth_token, oauth_token_secret,
            twitter_name, twitter_id):
        return self._save_profile(KEY_SITE_PROFILE, oauth_token,
            oauth_token_secret, twitter_name, twitter_id)

    def save_user_profile(self, user, oauth_token, oauth_token_secret,
            twitter_name, twitter_id):
        return self._save_profile('user_profile:%s' % user.id, oauth_token,
            oauth_token_secret, twitter_name, twitter_id)

    def _save_profile(self, datastore_key, oauth_token, oauth_token_secret,
            twitter_name, twitter_id):
        profile = {
            KEY_OAUTH_TOKEN: oauth_token,
            KEY_OAUTH_TOKEN_SECRET: oauth_token_secret,
            KEY_TWITTER_NAME: twitter_name,
            KEY_TWITTER_ID: twitter_id,
        }
        self.datastore.set(datastore_key, profile)
        return profile

    def remove_site_profile(self):
        self.datastore.delete(KEY_SITE_PROFILE)

    def remove_user_profile(self, user):
        self.datastore.delete('user_profile:%s' % user.id)

    def get_credentials(self):
        if settings.EMBEDDED:
            return (
                getattr(settings, 'TWITTER_CONSUMER_KEY', ''),
                getattr(settings, 'TWITTER_CONSUMER_SECRET_KEY', ''),
            )
        return self.datastore.get(KEY_CONSUMER_KEY), self.datastore.get(KEY_CONSUMER_SECRET)

    def set_credentials(self, consumer_key, consumer_secret):
        self.datastore.set(KEY_CONSUMER_KEY, consumer_key)
        self.datastore.set(KEY_CONSUMER_SECRET, consumer_secret)

    def get_user_settings_form(self, user):
        return self.datastore.load_form(forms.UserSettingsForm, 'user_settings:%s' % user.id)

    def get_user_settings(self, user):
        return self.get_user_settings_form(user).initial

    def save_user_settings_form(self, user, form):
        self.datastore.save_form(form, 'user_settings:%s' % user.id)

    def _issue_system_tweet(self, event, settings, site_profile):
        kind = event.kind
        tweet = None
        append_url = bool(settings.get('append_url'))

        if kind == event.DRINK_POURED:
            if not settings.get('tweet_drink_events'):
                self.logger.info('Skipping system tweet for drink event %s: disabled by settings.' % event.id)
                return
            template = settings.get('drink_poured_template')

        elif kind == event.SESSION_STARTED:
            if not settings.get('tweet_session_events'):
                self.logger.info('Skipping system tweet for session start event %s: disabled by settings.' % event.id)
                return
            template = settings.get('session_started_template')

        elif kind == event.SESSION_JOINED:
            if not settings.get('tweet_session_events'):
                self.logger.info('Skipping system tweet for session join event %s: disabled by settings.' % event.id)
                return
            template = settings.get('session_joined_template')

        elif kind == event.KEG_TAPPED:
            if not settings.get('tweet_keg_events'):
                self.logger.info('Skipping system tweet for keg start event %s: disabled by settings.' % event.id)
                return
            template = settings.get('keg_started_template')

        elif kind == event.KEG_ENDED:
            if not settings.get('tweet_keg_events'):
                self.logger.info('Skipping system tweet for keg end event %s: disabled by settings.' % event.id)
                return
            template = settings.get('keg_ended_template')

        else:
            self.logger.info('Skipping unhandled event type: %s' % kind)
            return

        if kind in (event.DRINK_POURED, event.SESSION_JOINED):
            if event.user.is_guest() and not settings.get('include_guests'):
                self.logger.info('Skipping system tweet for event %s: guest pour.' % event.id)
                return

        image_url = None

        if event.drink and event.drink.picture and settings.get('include_pictures'):
            image_url = event.drink.picture.resized.url

        tweet = self._compose_tweet(event, template, append_url)

        if not tweet:
            return

        self.logger.info('Scheduling system tweet: %s' % tweet)
        self._schedule_tweet(tweet, site_profile, image_url)

    def _issue_user_tweet(self, event, site_settings):
        kind = event.kind
        user = event.user
        tweet = None
        append_url = bool(site_settings.get('append_url'))

        if kind not in (event.SESSION_JOINED, event.DRINK_POURED):
            self.logger.info('Skipping user tweet for event %s: unknown event.' % event)
            return

        profile = self.get_user_profile(user)
        if not profile:
            self.logger.info('Skipping user tweet for event %s: no twitter profile.' % event.id)
            return

        user_settings = self.get_user_settings(user)

        if kind == event.DRINK_POURED:
            if not user_settings.get('tweet_drink_events'):
                self.logger.info('Skipping drink tweet for event %s: disabled by user.' % event.id)
                return
            template = site_settings.get('user_drink_poured_template')

        elif kind == event.SESSION_JOINED:
            if not user_settings.get('tweet_session_events'):
                self.logger.info('Skipping session tweet for event %s: disabled by user.' % event.id)
                return
            template = site_settings.get('session_started_template')

        if event.drink.shout:
            template = event.drink.shout

        image_url = None
        if event.drink and event.drink.picture and user_settings.get('include_pictures'):
            image_url = event.drink.picture.resized.url

        tweet = self._compose_tweet(event, template, append_url)

        if not tweet:
            return

        self.logger.info('Scheduling tweet: %s' % tweet)
        self._schedule_tweet(tweet, profile, image_url)

    def _compose_tweet(self, event, template, append_url):
        kbvars = self.get_vars(event)
        tweet = self.expand_template(template, kbvars)
        if append_url:
            url = kbvars['url']
            tweet = truncate_tweet(tweet, TWEET_MAX_LEN_WITH_URL)
            tweet = '%s %s' % (tweet, url)
        return truncate_tweet(tweet)

    def _schedule_tweet(self, tweet, profile, image_url=None):
        if not profile:
            self.logger.warning('Empty profile, skipping tweet.')
            return
        self.logger.info('Scheduling tweet on @%s: %s' % (profile.get('twitter_name'), repr(tweet)))
        consumer_key, consumer_secret = self.get_credentials()
        oauth_token = profile.get(KEY_OAUTH_TOKEN)
        oauth_token_secret = profile.get(KEY_OAUTH_TOKEN_SECRET)

        with SuppressTaskErrors(self.logger):
            tasks.send_tweet.delay(consumer_key, consumer_secret, oauth_token, oauth_token_secret,
                tweet, image_url)

    def get_vars(self, event):
        kbsite = KegbotSite.get()

        username = ''
        if event.user:
            username = event.user.username

        url = ''
        if event.drink:
            url = event.drink.short_url()
        elif event.session:
            url = event.session.short_url()

        beverage_name = ''
        if event.drink and (event.drink.keg and event.drink.keg.type):
            beverage_name = event.drink.keg.type.name

        # Must be a keg event if we still have no beer name.
        if event.keg and event.keg.type and not beverage_name:
            beverage_name = event.keg.type.name
            if not url:
                url = event.keg.full_url()

        volume_str = ''
        if event.drink:
            volume_str = kbsite.format_volume(event.drink.volume_ml)

        kbvars = {
            'site_name': kbsite.title,
            'username': username,
            'url': url,
            'volume_str': volume_str,
            'beverage_name': beverage_name,
        }
        return kbvars

    def expand_template(self, template, kbvars):
        """Compiles a template from `kbvars` variables."""
        if not template:
            return ''
        template = template.replace('$DRINKER', kbvars.get('username', ''))
        template = template.replace('$VOLUME', kbvars.get('volume_str', ''))
        template = template.replace('$BEVERAGE', kbvars.get('beverage_name', ''))
        template = template.replace('$BEER', kbvars.get('beverage_name', ''))  # compatibility
        template = template.replace('$SITENAME', kbvars.get('site_name', ''))
        template = template.replace('$URL', kbvars.get('url', ''))
        return template

    def get_client(self):
        consumer_key, consumer_secret = self.get_credentials()
        client = TwitterClient()
        client.consumer = oauth.Consumer(consumer_key, consumer_secret)
        return client
