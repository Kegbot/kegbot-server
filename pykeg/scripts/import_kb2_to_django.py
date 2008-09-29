#!/usr/bin/env python

import sys
import datetime

import kb2_backend
from pykeg.core import models

new = {
  'brewer': {},
  'drink': {},
  'beertype': {},
  'beerstyle': {},
  'user' : {},
  'keg' : {},
}

def trace(fn):
  def wrapped():
    print fn.__name__, '...'
    return fn()
  return wrapped

def GetNewIdForOld(kind, id):
  ret = new[kind].get(id)
  if ret is None:
    print 'Warning: cannot locate previous %s id %s' % (kind, id)
    raise ValueError
  return ret

@trace
def MigrateSimple():
  for rl in kb2_backend.RelayLog.select(orderBy='time'):
    new_rl = models.RelayLog(name=rl.name, status=rl.status, time=rl.time)
    new_rl.save()

  for tl in kb2_backend.ThermoLog.select(orderBy='time'):
    new_tl = models.ThermoLog(name=tl.name, temp=tl.temp, time=tl.time)
    new_tl.save()

@trace
def MigrateBrewers():
  for b in kb2_backend.Brewer.select():
    new_b = models.Brewer(name=b.name,origin_country=b.origin_country,
      origin_state = b.origin_state,
      origin_city=b.origin_city,distribution=b.distribution, url=b.url,
      comment=b.comment)
    new_b.save()
    new['brewer'][b.id] = new_b.id

@trace
def MigrateBeerStyles():
  for b in kb2_backend.BeerStyle.select():
    n = models.BeerStyle(name=b.name)
    n.save()
    new['beerstyle'][b.id] = n.id


@trace
def MigrateBeerTypes():
  for b in kb2_backend.BeerType.select():
    n = models.BeerType(name=b.name, brewer_id=new['brewer'][b.brewer.id],
      style_id=new['beerstyle'][b.style.id],calories_oz=b.calories_oz or 0,
      carbs_oz=b.carbs_oz or 0, abv=b.abv or 0)
    n.save()
    new['beertype'][b.id] = n.id

@trace
def MigrateKegs():
  for b in kb2_backend.Keg.select():
    q = models.KegSize.objects.filter(volume__exact=b.full_volume)
    if len(q):
      new_size = q[0]
    else:
      new_size = models.KegSize(volume=b.full_volume)
      new_size.save()

    now = datetime.datetime.now()

    n = models.Keg(type_id=new['beertype'][b.type.id], size=new_size,
      startdate=b.startdate or now, enddate=b.enddate or now, channel=b.channel,
      status=b.status, description=b.description or '', origcost=b.origcost or 0)
    n.save()
    new['keg'][b.id] = n.id


@trace
def MigrateUsers():
  for b in kb2_backend.User.select():
    n = models.User(username=b.username)
    if b.email:
      n.email = b.email
    n.save()
    p = models.UserProfile(user=n, gender=b.gender, weight=b.weight or 0)
    p.save()
    new['user'][b.id] = n.id

@trace
def MigrateTokens():
  for b in kb2_backend.Token.select():
    now = datetime.datetime.now()
    try:
      new_user_id = GetNewIdForOld('user', b.id)
    except ValueError:
      continue
      #print 'Assigning to id 1'
      #new_user_id = 1
    n = models.Token(user_id=new_user_id, keyinfo=b.keyinfo,
      created=b.created or now)
    n.save()

@trace
def MigrateUserLabels():
  for b in kb2_backend.UserLabel.select():
    n = models.UserLabel(user=new['user'][b.user.id], labelname=b.labelname)
    n.save()

@trace
def MigrateDrinks():
  for b in kb2_backend.Drink.select(orderBy='id'):
    n = models.Drink(ticks=b.ticks, volume=b.volume, starttime=b.starttime,
      endtime=b.endtime, user_id=GetNewIdForOld('user', b.user.id),
      keg_id=GetNewIdForOld('keg', b.keg.id), status=b.status)
    n.save()
    new['drink'][b.id] = n.id

@trace
def MigrateBacs():
  for b in kb2_backend.BAC.select():
    try:
      new_user=GetNewIdForOld('user', b.user.id)
      new_drink=GetNewIdForOld('drink', b.drink.id)
    except:
      continue
    n = models.BAC(user_id=new_user,
      drink_id=new_drink, rectime=b.rectime,
      bac=b.bac)
    n.save()


kb2_backend.setup(sys.argv[1])


MigrateSimple()
MigrateBrewers()
MigrateBeerStyles()
MigrateBeerTypes()
MigrateKegs()

MigrateUsers()
MigrateTokens()

#MigrateUserLabels()
MigrateDrinks()
MigrateBacs()

