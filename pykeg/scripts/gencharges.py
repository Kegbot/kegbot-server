#!/usr/bin/env python

from pykeg.core import models
from pykeg.accounting import models as accounting_models
from pykeg.core import models as core_models

def KegStatementIdForDrink(drink):
  return '__keg_%i__user_%i__' % (drink.keg.id, drink.user.id)

def GetOrCreateKegStatementForDrink(drink):
  stmt_id = KegStatementIdForDrink(drink)
  q = accounting_models.BillStatement.objects.filter(statement_id=stmt_id)
  if len(q) == 1:
    return q[0]
  elif len(q) == 0:
    desc = 'Automatic bill for Keg #%i' % drink.keg.id
    stmt = accounting_models.BillStatement(user=drink.user, statement_id=stmt_id,
      statement_date=drink.keg.enddate, short_desc=desc, long_desc=desc)
    stmt.save()
    return stmt

  assert False

def ChargeFloatToCents(amt):
  return int(round(amt * 100))

def GenCharge(drink, stmt, markup_pct=0.05):
  c = accounting_models.DrinkCharge()
  c.statement = stmt
  c.user = drink.user
  c.drink = drink

  drink_pct = float(drink.volume) / float(drink.keg.full_volume())
  drink_cost_float = drink_pct * float(drink.keg.origcost)
  ext_float = drink_cost_float * markup_pct

  print "charging %.2f + %.2f for drink %i" % (drink_cost_float, ext_float,
    drink.id)

  c.base_funds = ChargeFloatToCents(drink_cost_float)
  c.ext_funds = ChargeFloatToCents(ext_float)

  return c

for drink in core_models.Drink.objects.all().order_by('id'):
  # skip existing charge
  q = accounting_models.DrinkCharge.objects.filter(drink=drink)
  if len(q):
    print "charge for drink %i exists, skipping" % (drink.id,)
    continue

  # get or create statement
  if drink.keg.status != 'online':
    stmt = GetOrCreateKegStatementForDrink(drink)
  else:
    stmt = None

  charge = GenCharge(drink, stmt)
  charge.save()
