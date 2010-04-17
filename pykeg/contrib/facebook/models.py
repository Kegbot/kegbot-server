import datetime
from django.db import models
from django.db.models.signals import post_save
from socialregistration import models as sr_models

PRIVACY_CHOICES = (
  ('EVERYONE', 'Everyone'),
  ('ALL_FRIENDS', 'Friends'),
  ('FRIENDS_OF_FRIENDS', 'Friends of Friends'),
  ('NETWORK_FRIENDS', 'Networks and Friends'),
  #('CUSTOM', 'Custom permissions'),
)

class FacebookSession(models.Model):
  """Stores the session id for a user."""
  profile = models.ForeignKey(sr_models.FacebookProfile, unique=True,
      related_name='session')
  session_id = models.CharField(max_length=255, blank=False, null=False)
  updated = models.DateTimeField(default=datetime.datetime.now)

  @classmethod
  def get_session(cls, request):
    if not hasattr(request, 'facebook'):
      raise ValueError, "no facebook"
      return None
    fb = request.facebook
    if not fb.uid:
      raise ValueError, "no uid"
      return None

    profile = sr_models.FacebookProfile.objects.get(uid=fb.uid)
    if not profile:
      raise ValueError, "no profile"
      return None

    session, new = FacebookSession.objects.get_or_create(profile=profile)
    if new or session.session_id != fb.session_key:
      session.session_id = fb.session_key
      session.save()

  def add_permission(self, perm):
    qs = self.profile.permission_set.filter(permission=perm)
    if not qs.count():
      perm = FacebookPermission(profile=self.profile, permission=perm)
      perm.save()

  def rm_permission(self, perm):
    qs = self.profile.permission_set.filter(permission=perm)
    if qs.count():
      qs.delete()

def profile_post_save(sender, instance, **kwargs):
  """Create default settings on new profile."""
  settings, new = FacebookSettings.objects.get_or_create(
      profile=instance)
post_save.connect(profile_post_save, sender=sr_models.FacebookProfile)

class FacebookPermission(models.Model):
  """Records a granted permission."""
  profile = models.ForeignKey(sr_models.FacebookProfile, unique=True,
      related_name='permission_set')
  permission = models.CharField(max_length=255, blank=False, null=False,
      unique=True)

class FacebookSettings(models.Model):
  profile = models.ForeignKey(sr_models.FacebookProfile, unique=True,
      related_name='settings')

  # stream.publish stuff
  # http://wiki.developers.facebook.com/index.php/Stream.publish
  publish_events = models.BooleanField(default=True,
      help_text='Post each drink to your wall.')
  include_link = models.BooleanField(default=True,
      help_text='Add a link to this kegbot when publishing to wall.')
  publish_status = models.BooleanField(default=False,
      help_text='Update status on start of a new drinking session.')

  privacy = models.CharField(max_length=64, choices=PRIVACY_CHOICES,
      default='ALL_FRIENDS',
      help_text='Privacy setting for drink posts.')


