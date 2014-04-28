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

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import Context
from django.template.loader import get_template

import logging

logger = logging.getLogger('util')

SEPARATOR = '---EMAIL-BLOCK---'


def build_message(to_address, template_name, context_dict):
    from_address = getattr(settings, 'EMAIL_FROM_ADDRESS', None)
    if not from_address:
        logger.error('EMAIL_FROM_ADDRESS is not available; aborting!')
        return None

    template = get_template(template_name)
    context = Context(context_dict)
    rendered = template.render(context)

    parts = (x.strip() for x in rendered.split(SEPARATOR))
    subject, body_plain, body_html, footer_plain, footer_html = parts
    body_plain += '\n\n' + footer_plain
    body_html += '\n\n' + footer_html

    message = EmailMultiAlternatives(subject, body_plain, from_address, [to_address])
    message.attach_alternative(body_html, "text/html")
    return message
