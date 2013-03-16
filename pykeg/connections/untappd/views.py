# Copyright 2012 Mike Wakerly <opensource@hoho.com>
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


from django.core.urlresolvers import reverse
from client import Untappd
from models import UntappdProfile
from forms import UnlinkUntappdForm
from socialregistration.views import OAuthRedirect, OAuthCallback, SetupCallback

class UntappdRedirect(OAuthRedirect):
    client = Untappd
    template_name = 'connections/untappd/untappd.html'

class UntappdCallback(OAuthCallback):
    client = Untappd
    template_name = 'connections/untappd/untappd.html'
    
    def get_redirect(self):
        return reverse('untappd:setup')

class UntappdSetup(SetupCallback):
    client = Untappd
    profile = UntappdProfile
    template_name = 'connections/untappd/untappd.html'
    
    def get_lookup_kwargs(self, request, client):
        return {'untappd': client.get_user_info()['user_name']}
