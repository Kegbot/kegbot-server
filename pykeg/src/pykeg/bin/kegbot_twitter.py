#!/usr/bin/env python

from pykeg.core import importhacks
from pykeg.contrib.twitter import app

__doc__ = app.__doc__

if __name__ == '__main__':
  app.TwitterApp.BuildAndRun()
