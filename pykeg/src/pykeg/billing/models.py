# -*- coding: latin-1 -*-
import datetime

from django.db import models

class Credit(models.Model):
  amount = models.FloatField()
  acceptor = models.ForeignKey('BillAcceptor', blank=True, null=True)
  user = models.ForeignKey('auth.User', related_name='credits', blank=True,
      null=True)
  date = models.DateTimeField(default=datetime.datetime.now)

  # Reference to funds source.
  source = models.CharField(max_length=128,
      choices = ( ('cash', 'Cash'),
                  ('credit', 'Owner Credit'),
                  ('charge', 'Credit Card'),
                  ('gcheckout', 'Google Checkout'),
      ),
      default = 'cash',
  )

  # Purely administrative field to indicate payment status.
  status = models.CharField(max_length=128,
      choices = ( ('pending', 'Pending'),
                  ('processing', 'Processing'),
                  ('complete', 'Complete'),
                  ('invalid', 'Invalid'),
                  ('cancelled', 'Cancelled'),
      ),
      default = 'complete',
  )


class BillAcceptor(models.Model):
  name = models.CharField(max_length=128)
  increment = models.FloatField(default=1.0)

  def __str__(self):
    return 'BillAcceptor "%s"' % (self.name,)
