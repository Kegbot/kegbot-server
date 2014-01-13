from django.core.mail import send_mail

from . import models

def email_empty_keg(keg, emailAddress):

	print emailAddress

	subject = "Keg nearly empty."

	body = "{0} left of {1} remaining. Might be a good time to order more.".format(keg.remaining_volume(), keg.type.name)

	print body

	send_mail(subject, body, 'kegbotadmin@kegbot.com', [emailAddress], fail_silently=False)

