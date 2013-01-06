'''
Created on May 11, 2012

@author: shane
'''
import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'pykeg.settings'

from google.appengine.ext.webapp import util
import django.core.handlers.wsgi

app = django.core.handlers.wsgi.WSGIHandler()

def main():
  util.run_wsgi_app(app)

if __name__ == '__main__':
  main()
