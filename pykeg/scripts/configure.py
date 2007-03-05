from ConfigParser import ConfigParser
import md5
import sys

sys.path.append('.')
sys.path.append('..')
import Backend


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
      #dbconn = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpass, db=dbdb)
      if dbpass != '':
         dbpass = ':'+dbpass
      uri = 'mysql://%s%s@%s/%s' % (dbuser, dbpass, dbhost, dbdb)
      print uri
      Backend.setup(uri)
      print 'Great! You weren\'t lying; I managed to connect to the DB. Onward we go!'
   except:
      print 'Ooops! I tried connecting with that config and it did not work.'
      print 'If you havent yet created the %s table, you might try doing so:' % dbdb
      print '  mysqladmin -u root create %s' % dbdb
      print 'I\'m going to quit, but maybe the following error will help you out.'
      print ''
      raise

   print "I'm now going to create the tables in the database."
   print ""
   prompt_if_ok("Ok to add tables to %s database?" % dbdb)
   Backend.create_tables()
   print "Tables created; setting defaults"
   print ""
   Backend.set_defaults()

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

   for (option, title, default, descr) in sqls:
      print 'Saving %s...' % (option,),
      Backend.Config.get(option).value = sqlvals[option]
      print 'done!'

   print ''

   print 'Now, we can set up the first user. By default, a user named "admin"'
   print 'ships with the code. We can change that to your name now, and assign'
   print 'it an iButton number (if you have one).'

   print ''
   prompt_if_ok('Continue with additional setup?')
   print ''

   print 'OK, lets get some information about you. First, select a drinker name.'
   print 'You can always change this later, but for now, this will be how you log'
   print 'in to the kegbot over the web, and so on.'

   print ''
   drinker_name = prompt('Drinker name? [admin]: ') or 'admin'
   print ''
   print ''

   print 'Hi there, %s!' % (drinker_name,)
   print 'Now, lets select a password for you. The default password is'
   print '"kegbotadmin", but you should probably change that.'

   print ''
   password = prompt('New admin password? [kegbotadmin]: ') or 'kegbotadmin'
   print ''
   print ''

   print 'Finally, we will add a token for the admin user. If you do not have an'
   print 'iButton system, or don\'t yet have an iButton, you can leave the default.'

   print ''
   ibid = prompt('iButton ID for admin? []: ') or ''
   print ''
   print ''

   print 'Before I save the new user, please check below to make sure it is right.'
   print ''
   print 'drinker name : %s' % (drinker_name,)
   print '    password : %s' % (password, )
   print '  ibutton id : %s' % (ibid,)

   print ''
   prompt_if_ok('OK to update the admin user?')
   print ''

   print 'Updating admin user...',
   admin = Backend.User.get(1)
   admin.username = drinker_name
   admin.password = md5.md5(password).hexdigest()
   print 'done!'

   print 'Adding admin token...',
   Backend.Token(user=admin, keyinfo=ibid)
   print 'done!'

   print ''

   print 'All set!'


if __name__ == '__main__':
   Main()
