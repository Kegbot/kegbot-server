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

"""Local Django authentication backend."""

import uuid

from django.db import IntegrityError
from django.contrib.auth.backends import ModelBackend

from pykeg.core import models
from pykeg.web.auth import AuthBackend
from pykeg.web.auth import UserExistsException
from pykeg.util.email import build_message


class LocalAuthBackend(ModelBackend, AuthBackend):

    def is_manager(self, user):
        return user.is_staff

    def set_is_manager(self, user, is_manager):
        if user.is_staff != is_manager:
            user.is_staff = is_manager
            user.save()

    def is_owner(self, user):
        return user.is_superuser

    def set_is_owner(self, user, is_owner):
        if user.is_superuser != is_owner:
            user.is_superuser = is_owner
            user.save()

    def register(self, email, username, password=None, photo=None):
        try:
            user = models.User.objects.create(username=username, email=email)
        except IntegrityError as e:
            raise UserExistsException(e)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
            user.activation_key = str(uuid.uuid4()).replace('-', '')

        if photo:
            pic = models.Picture.objects.create(user=user)
            pic.image.save(photo.name, photo)
            pic.save()
            user.mugshot = pic

        user.save()

        kbsite = models.KegbotSite.get()
        template = None

        if user.activation_key:
            # Needs further activation: send activation e-mail.
            template = 'registration/email_activate_registration.html'
            url = kbsite.reverse_full('activate-account', args=(),
                kwargs={'activation_key': user.activation_key})
        elif email:
            # User already activated, send "complete" email.
            template = 'registration/email_registration_complete.html'
            url = kbsite.reverse_full('kb-account-main', args=(), kwargs={})

        if template:
            context = {
                'site_name': kbsite.title,
                'url': url,
            }
            message = build_message(email, template, context)
            if message:
                message.send(fail_silently=True)

        return user
