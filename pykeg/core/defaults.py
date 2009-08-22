from pykeg.core import models

def db_is_installed():
  try:
    version = models.Config.objects.get(key='db.schema_version')
    return True
  except models.Config.DoesNotExist:
    return False

def new_user(username, gender="male", weight=180):
   u = models.User(username=username)
   u.save()
   u.set_password(username)
   u.save()
   p = models.UserProfile(user=u, gender=gender, weight=weight)
   p.save()
   return u

def add_label(user, labelname):
  res = models.UserLabel.objects.filter(labelname__exact=labelname)
  if len(res):
    l = res[0]
  else:
    l = models.UserLabel(labelname=labelname)
    l.save()
  user.get_profile().labels.add(l)

def set_defaults():
   """ default values (contents may change with schema) """
   if db_is_installed():
     raise RuntimeError, "Database is already installed."

   # config table defaults
   default_config = (
      ('logging.logfile', 'keg.log'),
      ('logging.logformat', '%(asctime)s %(levelname)-8s (%(name)s) %(message)s'),
      ('logging.use_logfile', 'true'),
      ('logging.use_stream', 'true'),
      ('db.schema_version', str(models.SCHEMA_VERSION)),
   )
   for key, val in default_config:
      rec = models.Config(key=key, value=val)
      rec.save()

   # user defaults
   guest_user = new_user('guest')

   # brewer defaults
   unk_brewer = models.Brewer(name='Unknown Brewer')
   unk_brewer.save()

   # beerstyle defaults
   unk_style = models.BeerStyle(name='Unknown Style')
   unk_style.save()

   # beertype defaults
   unk_type = models.BeerType(name="Unknown Beer", brewer=unk_brewer, style=unk_style)
   unk_type.save()

   # userlabel defaults
   add_label(guest_user, '__default_user__')
   add_label(guest_user, '__no_bac__')
