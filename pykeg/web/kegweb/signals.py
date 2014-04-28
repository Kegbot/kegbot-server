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

from django.contrib.auth.signals import user_logged_in
from django.contrib.auth.signals import user_logged_out
from django.contrib import messages


def on_logged_in(sender, user, request, **kwargs):
    messages.add_message(request, messages.INFO, 'You are now logged in!',
      fail_silently=True)
user_logged_in.connect(on_logged_in)


def on_logged_out(sender, user, request, **kwargs):
    messages.add_message(request, messages.INFO, 'You have been logged out.',
      fail_silently=True)
user_logged_out.connect(on_logged_out)
