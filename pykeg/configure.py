import sys

try:
   import MySQLdb
except:
   print 'Eek! You do not seem to have MySQLdb, aka mysql-python, installed.'
   print 'Please install this and try again.'

from ConfigParser import ConfigParser

sqls = [ (  'devices.lcd', 
            'LCD display device',
            '/dev/null',
            'This device specifies where your matrix-orbital compatible LCD '
            'is located. Default is no LCD.' ),
         (  'devices.onewire',
            '1-wire (iButton) reader device',
            '/dev/null',
            'This path specifies where your USB or Serial 1-wire reader '
            'is located. Typically this is a serial port, such as '
            '/dev/ttyS0. Default is no device' ),
         (  'devices.flow',
            'Kegboard Device',
            '/dev/flow',
            'This path specifies where your kegboard controller is located. '
            'Typically this will be a serial or USB port, such as '
            '/dev/ttyS0 or /dev/usb/tts/0. Default is /dev/flow.' ),
         (  'ui.keypad_pipe',
            'USB keypad input device',
            '/dev/null',
            'If you are using a USB keypad for input, it must send its data '
            'to a special device file so we can read it. Typically this would '
            'be /dev/input/event0. If you do not have such hardware '
            'or do not know what this is, the default here is fine.' ),
      ]

def wrap(text, width):
    """
    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/148061
    A word-wrap function that preserves existing line breaks
    and most spaces in the text. Expects that existing line
    breaks are posix newlines (\n).
    """
    return reduce(lambda line, word, width=width: '%s%s%s' %
                  (line,
                   ' \n'[(len(line)-line.rfind('\n')-1
                         + len(word.split('\n',1)[0]
                              ) >= width)],
                   word),
                  text.split(' ')
                 )

def prompt(msg):
   return raw_input(msg)

def prompt_if_ok(msg):
   ret = raw_input(msg + ' [Y/n]: ')
   if ret.lower().startswith('n'):
      print 'You said NO, so we are quitting!'
      sys.exit(0)

def Main():
   print 'Welcome to the kegbot configurator! You should be running this if you'
   print 'are setting up a new kegbot install *for the first time*. If you already'
   print 'have a working install, you are probably better off using something else.'
   print ''

   prompt_if_ok('OK to continue?')

   try:
      f = open('keg.cfg')
      flines = f.readlines()
      f.close()
      config = ConfigParser()
      config.read('keg.cfg')
   except:
      print 'Oops! It looks like I cannot read the file "keg.cfg" in the current'
      print 'directory. I need this file for database information. Please fix this'
      print 'and try again.'
      raise
      sys.exit(1)

   print "I'm going to need to connect to your database, so we need to be sure"
   print "that is setup properly. I'm using the data in keg.cfg to connect; does"
   print "this look correct?"
   print ''
   for line in flines:
      print '   %s' % (line.strip(),)
   print ''

   prompt_if_ok('Is keg.cfg (printed above) correct?')

   print ''

   try:
      dbhost = config.get('DB','host')
      dbuser = config.get('DB','user')
      dbdb   = config.get('DB','db')
      dbpass = config.get('DB','password')
      dbconn = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpass, db=dbdb)
      print 'Great! You weren\'t lying; I managed to connect to the DB. Onward we go!'
   except:
      print 'Ooops! I tried connecting with that config and it did not work.'
      print 'I\'m going to quit, but maybe the following error will help you out.'
      print ''
      raise

   print ''

   print "Now, let's start by configuring some default devices. I'm going to need"
   print "to know where the various devices you may have attached live."
   print ''

   prompt('Press return to continue.')
   print ''

   sqlvals = {}
   for (option, title, default, descr) in sqls:
      print title
      print '-'*len(title)
      print wrap(descr, 80)
      print ''
      val = prompt('%s [%s]: ' % (title, default))
      sqlvals[option] = val or default
      print ''
      print ''
      print ''

   print '-'*80
   print 'Great! We\'re almost ready to save your new config. Before we do, please'
   print 'take a look at the values below and ensure they are what you want.'
   print
   
   maxlen = max([len(x[0]) for x in sqls])
   for (option, title, default, descr) in sqls:
      print '%s : %s' % (option.rjust(maxlen), sqlvals[option])

   print ''
   prompt_if_ok('OK with above?')
   print ''

   c = dbconn.cursor()
   for (option, title, default, descr) in sqls:
      q = """ UPDATE `config` SET `value`='%s' WHERE `key`='%s' """ % (MySQLdb.escape_string(sqlvals[option]), MySQLdb.escape_string(option))
      print 'Saving %s...' % (option,),
      c.execute(q)
      print 'done!'



if __name__ == '__main__':
   Main()
