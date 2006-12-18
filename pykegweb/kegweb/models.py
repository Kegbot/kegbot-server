from django.db import models


class KegbotUser(models.Model):
   class Meta:
      db_table = "users"

   class Admin:
      pass

   username = models.CharField(maxlength=32)
   email = models.EmailField()
   im_aim = models.CharField(maxlength=128)
   password = models.CharField(maxlength=128)
   gender = models.CharField(maxlength=16, choices = (
      ('male', 'male'),
      ('female', 'female'),
      ), default = 'male')
   weight = models.FloatField(max_digits=6, decimal_places=2)

   # grants, tokens, labels

   def __str__(self):
      return self.username

   def LeadersByVolume(self):
      return self.get_list()

   def VolumeByKeg(self):
      return 123

class Brewer(models.Model):
   class Meta:
      db_table = "brewers"

   class Admin:
      pass

   name = models.CharField(maxlength=128)
   origin_country = models.CharField(maxlength=128)
   origin_state = models.CharField(maxlength=128)
   origin_city = models.CharField(maxlength=128)
   distribution = models.CharField(maxlength=128,
         choices = ( ('retail', 'retail'),
                     ('homebrew', 'homebrew'),
                     ('unknown', 'unknown'),
         ),
   )
   url = models.URLField(verify_exists=False)
   comment = models.TextField()

   def __str__(self):
      return "%s (%s, %s, %s)" % (self.name, self.origin_city,
            self.origin_state, self.origin_country)


class BeerStyle(models.Model):
   class Meta:
      db_table = "beerstyles"

   class Admin:
      pass

   name = models.CharField(maxlength=128)

   def __str__(self):
      return self.name


class BeerType(models.Model):
   class Meta:
      db_table = "beertypes"

   class Admin:
      list_display=('name', 'brewer', 'style')

   name = models.CharField(maxlength=128)
   brewer = models.ForeignKey(Brewer)
   style = models.ForeignKey(BeerStyle)
   calories_oz = models.FloatField(max_digits=6,decimal_places=2)
   carbs_oz = models.FloatField(max_digits=6,decimal_places=2)
   abv = models.FloatField(max_digits=6, decimal_places=6)

   def __str__(self):
      return "%s by %s" % (self.name, self.brewer)


class Keg(models.Model):
   class Meta:
      db_table = "kegs"

   class Admin:
      list_display = ('id', 'type')

   type = models.ForeignKey(BeerType)
   full_volume = models.IntegerField()
   startdate = models.DateTimeField('start date')
   enddate = models.DateTimeField('end date')
   channel = models.IntegerField()
   status = models.CharField(maxlength=128, choices=(
      ('online', 'online'),
      ('offline', 'offline'),
      ('coming soon', 'coming soon')))
   description = models.CharField(maxlength=128)
   origcost = models.FloatField(max_digits=6,decimal_places=2)

   def __str__(self):
      return "Keg #%s - %s" % (self.id, self.type)


class Drink(models.Model):
   class Meta:
      db_table = "drinks"

   class Admin:
      pass

   ticks = models.PositiveIntegerField()
   volume = models.PositiveIntegerField()
   starttime = models.DateTimeField('drink start')
   endtime = models.DateTimeField('drink end')
   user = models.ForeignKey(KegbotUser)
   keg = models.ForeignKey(Keg)
   status = models.CharField(maxlength=128, choices = (
      ('valid', 'valid'),
      ('invalid', 'invalid'),
      ), default = 'valid')

   def __str__(self):
      return "Drink %s by %s" % (self.id, self.user)


class Policy(models.Model):
   class Meta:
      db_table = "policies"

   class Admin:
      pass

   type = models.CharField(maxlength=32, choices=(
      ('fixed-cost', 'fixed-cost'),
      ('free', 'free'),
      ), default = 'fixed-cost')
   unitcost = models.FloatField(max_digits=6, decimal_places=4)
   unitvolume = models.PositiveIntegerField()
   description = models.TextField()

   def __str__(self):
      return self.description


class Grant(models.Model):
   class Meta:
      db_table = "grants"

   class Admin:
      pass

   user = models.ForeignKey(KegbotUser)
   expiration = models.CharField(maxlength=128, choices = (
      ('none', 'none'),
      ('time', 'time'),
      ('volume', 'volume'),
      ('drinks', 'drinks'),
      ), default = "none")
   status  = models.CharField(maxlength=128, choices = (
      ('active', 'active'),
      ('expired', 'expired'),
      ('deleted', 'deleted'),
      ), default = 'active')
   policy = models.ForeignKey(Policy)
   exp_volume = models.PositiveIntegerField(default=0)
   exp_time = models.DateTimeField()
   exp_drinks = models.PositiveIntegerField(default=0)
   total_volume = models.PositiveIntegerField(default=0)
   total_drinks = models.PositiveIntegerField()

   def __str__(self):
      return "%s for %s" % (self.policy, self.user)


class Token(models.Model):
   class Meta:
      db_table = "tokens"

   class Admin:
      pass

   user = models.ForeignKey(KegbotUser)
   keyinfo = models.TextField()
   created = models.DateTimeField()

   def __str__(self):
      return "Token %s for %s" % (self.id, self.user)


class BAC(models.Model):
   class Meta:
      db_table = "bacs"

   class Admin:
      pass

   user = models.ForeignKey(KegbotUser)
   drink = models.ForeignKey(Drink)
   rectime = models.DateTimeField()
   bac = models.FloatField(max_digits=6, decimal_places=4)

   def __str__(self):
      return "%s BAC at %s" % (self.user, self.drink)


class GrantCharge(models.Model):
   class Meta:
      db_table = "grantcharges"

   class Admin:
      pass

   grant = models.ForeignKey(Grant)
   drink = models.ForeignKey(Drink)
   user = models.ForeignKey(KegbotUser)
   volume = models.PositiveIntegerField()


class Binge(models.Model):
   class Meta:
      db_table = "binges"

   class Admin:
      pass

   def __str__(self):
      return "binge %s by %s (%s to %s)" % (self.id, self.user, self.starttime, self.endtime)

   user = models.ForeignKey(KegbotUser)
   startdrink = models.ForeignKey(Drink, related_name='start')
   enddrink = models.ForeignKey(Drink, related_name='end')
   volume = models.PositiveIntegerField()
   starttime = models.DateTimeField()
   endtime = models.DateTimeField()


class UserPic(models.Model):
   class Meta:
      db_table = "userpics"

   class Admin:
      pass

   user = models.ForeignKey(KegbotUser)
   filetype = models.CharField(maxlength=12)
   modified = models.DateTimeField()
   #data = models.ImageField(upload_to='/tmp') # XXX
   data = models.TextField()


class Thermolog(models.Model):
   class Meta:
      db_table = "thermolog"

   class Admin:
      pass

   name = models.CharField(maxlength=128)
   temp = models.FloatField(max_digits=6, decimal_places=3)
   time = models.DateTimeField()


class RelayLog(models.Model):
   class Meta:
      db_table = "relaylog"

   class Admin:
      pass

   name = models.CharField(maxlength=128)
   status = models.CharField(maxlength=32)
   time = models.DateTimeField()

class UserLabel(models.Model):
   class Meta:
      db_table = "userlabels"

   class Admin:
      pass

   user = models.ForeignKey(KegbotUser)
   labelname = models.CharField(maxlength=128)

