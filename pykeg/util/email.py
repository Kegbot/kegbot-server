from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core import signing
from django.template.loader import get_template

import logging

logger = logging.getLogger("util")

SEPARATOR = "---EMAIL-BLOCK---"

EMAIL_CHANGE_MAX_AGE = 60 * 60 * 24


def build_message(to_address, template_name, context):
    from_address = getattr(settings, "DEFAULT_FROM_EMAIL", None)
    if not from_address:
        logger.error("DEFAULT_FROM_EMAIL is not available; aborting!")
        return None

    template = get_template(template_name)
    rendered = template.render(context)

    parts = (x.strip() for x in rendered.split(SEPARATOR))
    subject, body_plain, body_html, footer_plain, footer_html = parts
    body_plain += "\n\n" + footer_plain
    body_html += "\n\n" + footer_html

    message = EmailMultiAlternatives(subject, body_plain, from_address, [to_address])
    message.attach_alternative(body_html, "text/html")
    return message


def build_email_change_token(user, new_address):
    token = signing.dumps({"uid": user.id, "new_address": new_address,})
    return token


def verify_email_change_token(user, token, max_age=EMAIL_CHANGE_MAX_AGE):
    try:
        token = signing.loads(token, max_age=max_age)
        if token.get("uid") != user.id:
            raise ValueError("User ID does not match.")
    except signing.BadSignature as e:
        raise ValueError(e)

    return token.get("uid"), token.get("new_address")
