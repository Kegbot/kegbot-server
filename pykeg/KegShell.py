import os, string, readline, time

class KegShell(threading.Thread):
   def __init__(self,owner):
      threading.Thread.__init__(self)
      self.owner = owner
      self.commands = ['status','quit','adduser','showlog','hidelog', 'bot', 'showtemp']

      # setup readline to do fancy tab completion!
      self.completer = Completer()
      self.completer.set_choices(self.commands)
      readline.parse_and_bind("tab: complete")
      readline.set_completer(self.completer.complete)

   def run(self):
      while 1:
         try:
            input = self.prompt()
            tokens = string.split(input,' ')
            cmd = string.lower(tokens[0])
         except:
            raise

         if cmd == 'quit':
            self.owner.quit()
            return

         if cmd == 'showlog':
            self.owner.verbose = 1

         if cmd == 'status':
            print self.owner.fc.status

         if cmd == 'hidelog':
            self.owner.verbose = 0

         if cmd == 'bot':
            try:
               subcmd = tokens[1]
               if subcmd == 'go':
                  self.owner.bm.botGo("aimbot")
               elif subcmd == 'stop':
                  self.owner.bm.botStop("aimbot")
               elif subcmd == 'say':
                  user  = tokens[2]
                  msg = raw_input('message: ')
                  self.owner.aimbot.do_SEND_IM(user,msg)
            except:
               pass

         if cmd == 'showtemp':
            try:
               temp = self.owner.tempsensor._temps[1]
               print "last temp: %.2i C / %.2i F" % (temp,toF(temp))
            except:
               pass

         if cmd == 'adduser':
            user = self.adduser()
            username,admin,aim,initib = user

            print "got user: %s" % str(username)

            try:
               self.owner.addUser(username,init_ib = initib,admin=admin,aim=aim)
               print "added user successfully"
            except:
               print "failed to create user"
               raise

   def prompt(self):
      try:
         prompt = "[KEGBOT] "
         cmd = raw_input(prompt)
      except:
         # this exception may be nasty. in particular, if the tty dies, then
         # this will loop forever. as a temporary fix, the sleep here will keep
         # it from going completely nuts
         cmd = ""
         time.sleep(2.0)
      return cmd

   def adduser(self):
      print "please type the unique username for this user."
      username = raw_input("username: ")
      print "will this user have admin privileges?"
      admin = raw_input("admin [y/N]: ")
      print "please type the user's aim name, if known"
      aim = raw_input("aim name [none]: ")
      print "would you like to associate a particular beerkey with this user?"
      print "here are the buttons i see on the network:"
      count = 0
      for ib in self.owner.ibs:
         print "[%i] %s (%s)" % (count,ib.name,ib.read_id())
         count = count+1
      key = raw_input("key number [none]: ")
      try:
         ib = self.owner.ibs[int(key)]
         key = ib.read_id()
         print "selected %s" % key
      except:
         key = None

      if string.lower(admin)[0] == 'y':
         admin = 1
      else:
         admin = 0

      if aim == "" or aim == "\n":
         aim = None

      if key == "" or key == "\n":
         key = None

      return (username,admin,aim,key)


class Completer:
   def __init__(self):
      self.list = []

   def complete(self, text, state):
      if state == 0:
         self.matches = self.get_matches(text)
      try:
         return self.matches[state]
      except IndexError:
         return None

   def set_choices(self, list):
       self.list = list

   def get_matches(self, text):
      matches = []
      for x in self.list:
         if string.find(x, text) == 0:
            matches.append(x)
      return matches


