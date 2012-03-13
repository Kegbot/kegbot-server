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

from django.contrib import admin
from . import models
from django.conf import settings
import pykeg.core.importhacks
from django.forms import ModelForm, PasswordInput, CharField
from django.core.exceptions import ValidationError
from hashlib import md5

import urllib, urllib2, base64

try:
  import json
except ImportError:
  try:
    import simplejson as json
  except ImportError:
    try:
      from django.utils import simplejson as json
    except ImportError:
      raise ImportError, "Unable to load a json library"


class UserUntappdLinkAdminForm(ModelForm):
  password = CharField(label='Untappd Password',  widget=PasswordInput, required=True)

  class Meta:
    model = models.UserUntappdLink

  def __init__(self, *args, **kwargs):
    super(UserUntappdLinkAdminForm, self).__init__(*args, **kwargs)

  def clean(self):
    cleaned_data = super(UserUntappdLinkAdminForm, self).clean()
    
    self.password_hash = md5(cleaned_data['password']).hexdigest()
    
    if settings.UNTAPPD_API_KEY == None:
      raise ValidationError('Untappd API key is not set. Please add your UNTAPPD_API_KEY to your common_settings.py file.')
    
    req = urllib2.Request("http://api.untappd.com/v3/user?key=" + settings.UNTAPPD_API_KEY)
    
    base64string = base64.encodestring('%s:%s' % (cleaned_data['untappd_name'], self.password_hash))[:-1]
    authheader =  "Basic %s" % base64string
    req.add_header("Authorization", authheader)
            
    try:
      response = urllib2.urlopen(req)
    
    except urllib2.HTTPError:
      self.error_messages = {'response_error' : 'There was a problem validating the password with Untappd. Please check the username / password or try again later.'}
      raise ValidationError(self.error_messages['response_error'])
              
    try:
      response = json.loads(response.read())
      
      if response.has_key('error'):
        self.error_messages = {'response_error' : str(response['error'])}
        raise ValidationError(self.error_messages['response_error'])
    
    except KeyError, ValueError:
      self.error_messages = {'response_error' : 'There was a problem validating the password with Untappd. Try again later.'}
      raise ValidationError(self.error_messages['response_error'])
    
    return cleaned_data

  def save(self, commit=True):    
    model = super(UserUntappdLinkAdminForm, self).save(commit=False)
    model.untappd_password_hash = self.password_hash
      
    if commit:
      model.save()
    
    return model

class UserUntappdLinkAdmin(admin.ModelAdmin):
  def get_readonly_fields(self, request, obj=None):
    return self.readonly_fields + ('untappd_password_hash',)
    
  list_display = ('untappd_name', 'user_profile')
  form = UserUntappdLinkAdminForm
    

admin.site.register(models.UserUntappdLink, UserUntappdLinkAdmin)

