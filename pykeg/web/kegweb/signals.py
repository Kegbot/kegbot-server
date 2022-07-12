from django.contrib import messages
from django.contrib.auth.signals import user_logged_in, user_logged_out


def on_logged_in(sender, user, request, **kwargs):
    messages.add_message(request, messages.INFO, "You are now logged in!", fail_silently=True)


user_logged_in.connect(on_logged_in)


def on_logged_out(sender, user, request, **kwargs):
    messages.add_message(request, messages.INFO, "You have been logged out.", fail_silently=True)


user_logged_out.connect(on_logged_out)
