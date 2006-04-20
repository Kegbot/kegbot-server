import sys

import MySQLdb
import ConfigParser

config = ConfigParser.RawConfigParser()
config.read('keg.cfg')
dbhost = config.get('DB','host')
dbuser = config.get('DB','user')
dbdb   = config.get('DB','db')
dbpass = config.get('DB','password')
dbconn = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpass, db=dbdb)

sys.path.append('.')
import Backend
import util
import sqlobject

db_uri = 'mysql://%s:%s@%s/%s' % (dbuser, dbpass, dbhost, dbdb)
Backend.setup(db_uri)
Backend.set_defaults()
