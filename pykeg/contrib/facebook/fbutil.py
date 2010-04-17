from django.conf import settings

import facebook

def profile_for_user(user):
  profile = user.facebookprofile_set.all()
  if not profile:
    return None
  return profile[0]

def session_for_user(user):
  profile = profile_for_user(user)
  if not profile:
    return None
  session = profile.session.all()
  if not session:
    return None
  return session[0]

def settings_for_user(user):
  profile = profile_for_user(user)
  if not profile:
    return None
  settings = profile.settings.all()
  if not settings:
    return None # should never happen, due to post-save signal
  return settings[0]

def stream_publish(user, **kwargs):
  session = session_for_user(user)
  if not session:
    raise ValueError, "No session."
  fb = facebook.Facebook(settings.FACEBOOK_API_KEY,
      settings.FACEBOOK_SECRET_KEY)
  fb.session_key = session.session_id
  fb.session_key_expires = 0
  return fb.stream.publish(**kwargs)

