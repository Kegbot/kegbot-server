from pykeg.util.email import build_message
from pykeg.core import models as core_models
from pykeg.notification.backends.base import BaseNotificationBackend

import logging

logger = logging.getLogger("email-notification")


class EmailNotificationBackend(BaseNotificationBackend):
    @classmethod
    def name(cls):
        return "pykeg.notification.backends.email.EmailNotificationBackend"

    def notify(self, event, user):
        logger.info("Event %s -> user %s" % (event, user))

        to_address = user.email
        if not to_address:
            logger.warning("No e-mail address available for user %s" % user)
            return

        context = {}
        template_name = None

        kbsite = core_models.KegbotSite.get()
        context["site_name"] = kbsite.title
        context["site_url"] = kbsite.base_url()
        context["settings_url"] = context["site_url"] + "/account"

        context["drink"] = event.drink
        context["keg"] = event.keg
        context["session"] = event.session

        if event.kind == core_models.SystemEvent.KEG_TAPPED:
            template_name = "notification/email_keg_tapped.html"
            context["url"] = event.keg.full_url()
        elif event.kind == core_models.SystemEvent.KEG_ENDED:
            template_name = "notification/email_keg_ended.html"
            context["url"] = event.keg.full_url()
        elif event.kind == core_models.SystemEvent.SESSION_STARTED:
            template_name = "notification/email_session_started.html"
            context["url"] = event.session.short_url()
        elif event.kind == core_models.SystemEvent.KEG_VOLUME_LOW:
            template_name = "notification/email_keg_volume_low.html"
            context["url"] = event.keg.full_url()
        else:
            logger.info("Skipping unknown event type: %s" % event.kind)
            return

        message = build_message(to_address, template_name, context)
        if not message:
            logger.warning("Aborting due to error building message.")
            return
        self.send_message(message)

    def send_message(self, message):
        logger.info("Sending message: %s" % message)
        message.send(fail_silently=True)
