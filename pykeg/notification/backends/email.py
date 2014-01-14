# Copyright 2014 Mike Wakerly <opensource@hoho.com>
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

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.mail import send_mail
from django.template import Context
from django.template.loader import get_template

from pykeg.core import models as core_models
from pykeg.notification.backends.base import BaseNotificationBackend

import logging

logger = logging.getLogger('email-notification')

class EmailNotificationBackend(BaseNotificationBackend):
    def notify(self, event, user):
        logger.info('Event %s -> user %s' % (event, user))

        to_address = user.email
        if not to_address:
            logger.warning('No e-mail address available for user %s' % user)
            return

        context = {}
        template_name = None

        site_settings = core_models.SiteSettings.get()
        context['site_name'] = site_settings.title
        context['site_url'] = site_settings.base_url()
        context['settings_url'] = context['site_url'] + '/account'

        context['drink'] = event.drink
        context['keg'] = event.keg
        context['session'] = event.session

        if event.kind == core_models.SystemEvent.KEG_TAPPED:
            template_name = 'notification/email_keg_tapped.html'
            context['url'] = event.keg.full_url()
        elif event.kind == core_models.SystemEvent.KEG_ENDED:
            template_name = 'notification/email_keg_ended.html'
            context['url'] = event.keg.full_url()
        elif event.kind == core_models.SystemEvent.SESSION_STARTED:
            template_name = 'notification/email_session_started.html'
            context['url'] = event.session.short_url()
        elif event.kind == core_models.SystemEvent.KEG_VOLUME_LOW:
            template_name = 'notification/email_keg_volume_low.html'
            context['url'] = event.keg.full_url()
        else:
            logger.info('Skipping unknown event type: %s' % event.kind)
            return

        message = build_message(to_address, template_name, context)
        if not message:
            logger.warning('Aborting due to error building message.')
            return
        self.send_message(message)

    def send_message(self, message):
        logger.info('Sending message: %s' % message)
        message.send()

def build_message(to_address, template_name, context_dict):
    from_address = getattr(settings, 'EMAIL_FROM_ADDRESS', None)
    if not from_address:
        logger.error('EMAIL_FROM_ADDRESS is not available; aborting!')
        return None

    template = get_template(template_name)
    context = Context(context_dict)
    rendered = template.render(context)

    parts = (x.strip() for x in rendered.split('---EMAIL-BLOCK---'))
    subject, body_plain, body_html, footer_plain, footer_html = parts
    body_plain += '\n\n' + footer_plain
    body_html += '\n\n' + footer_html

    message = EmailMultiAlternatives(subject, body_plain, from_address, [to_address])
    message.attach_alternative(body_html, "text/html")
    return message