import datetime

from pykeg.core import models, units
from django.contrib.auth.models import User

from pykeg.core.Devices import Kegboard

def new_user(username, gender="male", weight=180):
   u = User(username=username)
   u.save()
   p = models.UserProfile(user=u, gender=gender, weight=weight)
   p.save()
   return u


def set_data():
   """ default values (contents may change with schema) """
   sn = models.Brewer(name='Sierra Nevada Brewing Company',
         origin_country='USA',
         origin_state='California',
         origin_city='Chico',
         distribution='retail',
         url='http://www.sierranevada.com/')
   sn.save()

   an = models.Brewer(name='Anchor Brewing Company',
         origin_country='USA',
         origin_state='California',
         origin_city='San Francisco',
         distribution='retail',
         url='http://www.anchorsteam.com/')
   an.save()

   # beerstyle defaults
   pale_ale = models.BeerStyle(name='Pale Ale')
   pale_ale.save()

   # beertype defaults
   sn_pa = models.BeerType(name="Sierra Nevada Pale Ale",
         brewer=sn,
         style=pale_ale,
         calories_oz=10,
         carbs_oz=10,
         abv=5.5)
   sn_pa.save()

   as_pa = models.BeerType(name="Anchor Liberty Ale",
         brewer=an,
         style=pale_ale,
         calories_oz=10,
         carbs_oz=10,
         abv=5.0)
   as_pa.save()

   usernames = ['abe', 'bort', 'charlie']
   users = []
   for name in usernames:
      u = new_user(name)
      users.append(u)

   half_barrel = models.KegSize(name="half barrel", volume=10000)
   half_barrel.save()

   k = models.Keg(type=as_pa, size=half_barrel, status='online', channel=0,
                  origcost=100)
   k.save()

   drink_base = datetime.datetime(2007,1,1,8,0,0)
   drink_interval = datetime.timedelta(seconds=600)
   drink_num = 0
   drink_vols = []
   for size in (11.5, 12.5, 16, 11, 12, 22):
     drink_vols.append(units.Quantity.FromUnits(units.UNITS.Ounce, size))

   # generate some drinks
   for rounds in range(3):
      for u in users:
         start = drink_base + drink_num*drink_interval
         end = start + datetime.timedelta(seconds=10)
         vol = drink_vols[drink_num%len(drink_vols)]
         drink = models.Drink(ticks=vol.ConvertTo.KbMeterTick,
                              volume=vol.Amount(units.RECORD_UNIT),
                              starttime=start, endtime=end, user=u, keg=k,
                              status='valid')
         drink.save()
         models.BAC.ProcessDrink(drink)
         models.Binge.Assign(drink)
         drink_num += 1

if __name__ == '__main__':
   set_data()
