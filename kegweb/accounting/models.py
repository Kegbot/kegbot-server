# -*- coding: latin-1 -*-
import datetime

from django.db import models
from django.contrib import admin

class AbstractFundsModel(models.Model):
  class Meta:
    abstract = True

  user = models.ForeignKey('auth.User')
  base_funds = models.IntegerField(default=0)
  ext_funds = models.IntegerField(default=0)
  tax_funds = models.IntegerField(default=0)
  handling_funds = models.IntegerField(default=0)

  def TotalFunds(self):
    return self.base_funds + self.ext_funds + self.tax_funds + self.handling_funds

  def TotalFundsStr(self):
    tot = self.TotalFunds()
    if tot < 100:
      return "%i¢" % tot
    else:
      return "$%.2f" % (tot/100.0)


class BillStatement(models.Model):
  user = models.ForeignKey('auth.User')
  statement_date = models.DateTimeField(default=datetime.datetime.now)
  statement_id = models.CharField(max_length=128, unique=True)
  short_desc = models.CharField(max_length=128)
  long_desc = models.TextField()

  def __str__(self):
    return 'Statement for %s: "%s"' % (self.user, self.short_desc)

  def TotalFunds(self):
    drink_charge_sum = sum(d.TotalFunds() for d in self.drink_charges.all())
    misc_charge_sum = sum(m.TotalFunds() for m in self.misc_charges.all())
    return drink_charge_sum + misc_charge_sum

  def TotalFundsFloat(self):
    return self.TotalFunds() / 100.0

  def IsCredit(self):
    return self.TotalFunds() <= 0

admin.site.register(BillStatement)


class DrinkCharge(AbstractFundsModel):
  # The line item may not yet be associated with a statement, eg unbilled
  statement = models.ForeignKey(BillStatement, null=True, blank=True,
    related_name='drink_charges')
  drink = models.ForeignKey('core.Drink')

  def __str__(self):
    return '%s %s (keg %i drink %i)' % (self.user, self.TotalFundsStr(),
      self.drink.keg.id, self.drink.id)

  @classmethod
  def DoCharge(cls, drink, base=0, tax=0, handling=0):
    q = DrinkCharge.objects.filter(drink=drink)
    if len(q):
      raise ValueError, "Charge for drink already exists"
    c = DrinkCharge(drink=drink, base_charge=base, tax_charge=tax,
      handling_charge=handling)
    c.save()
    return c

admin.site.register(DrinkCharge)


class MiscCharge(AbstractFundsModel):
  # The line item may not yet be associated with a statement, eg unbilled
  statement = models.ForeignKey(BillStatement, null=True, blank=True,
    related_name='misc_charges')
  short_desc = models.CharField(max_length=128)
  long_desc = models.TextField()

admin.site.register(MiscCharge)


class Payment(AbstractFundsModel):
  # The |user| column inherited from AbstractFundsModel describes the account
  # receiving the payment credit. The |source_user| column describes the account
  # sending the funds (making the payment). These should often be the same user,
  # but |source_user| may be different when someone else picks up the tab, or
  # the admin gives a credit, etc.
  source_user = models.ForeignKey('auth.User', related_name='outgoing_payments')

  # A payment may associated with a statement, or simply added to the account
  # balance.
  statement = models.ForeignKey(BillStatement, null=True, blank=True)

  # Date the payment was posted
  payment_date = models.DateTimeField()

  # Reference to funds source.
  payment_funds_source = models.CharField(max_length=128,
      choices = ( ('cash', 'Cash'),
                  ('credit', 'Owner Credit'),
                  ('charge', 'Credit Card'),
                  ('gcheckout', 'Google Checkout'),
      ),
      default = 'cash',
  )

  # Space for a custom transaction id; may be specific to a funds source.
  transaction_id = models.CharField(max_length=256, null=True, blank=True)

  # Purely administrative field to indicate payment status.
  payment_status = models.CharField(max_length=128,
      choices = ( ('pending', 'Pending'),
                  ('processing', 'Processing'),
                  ('complete', 'Complete'),
                  ('invalid', 'Invalid'),
                  ('cancelled', 'Cancelled'),
      ),
      default = 'complete',
  )

  # Purely administrative field for scribbling a reason, if any, for
  # payment_status
  status_message = models.TextField(null=True, blank=True)

admin.site.register(Payment)
