from toc import TocTalk, BotManager
import aiml
import os.path
import re
import time
import marshal
from ConfigParser import ConfigParser

class KegAIMBot(TocTalk):
   def __init__(self, sn, pw, owner):
      TocTalk.__init__(self,sn,pw)
      self.owner = owner

      self._info = self.owner.config.get('AIM','profile') # (py-toc parameter)
      self._debug = 0 # critical debug messages (py-toc parameter)

      self.k = aiml.Kernel()

      # parameters
      self.typerate = self.owner.config.getfloat('Bot','typerate') # seconds

      # other stuff..
      os.chdir(self.owner.config.get('Bot','ai_dir'))
      brainfile = self.owner.config.get('Bot','save_brain')
      startupfile = self.owner.config.get('Bot','startup_file')
      startcommand = self.owner.config.get('Bot','startup_command')

      # bootstrap the brain: attempt to load a saved brain, else create (and
      # save) a new one
      if os.path.isfile(brainfile):
         self.k.bootstrap(brainFile = brainfile)
      else:
         self.k.bootstrap(learnFiles = startupfile, commands = startcommand)
         if self.owner.config.getboolean('Bot','do_save_brain'):
            self.k.saveBrain(brainfile)

      # load the defaults (eg, name). do this after the brain is loaded, just
      # in case they have changed.
      self.loadDefaults()

      # attempt to reload past sessions. this feature is somewhat staable in
      # pyaiml.
      try:
         self.loadSessions()
      except:
         pass

   def loadDefaults(self):
      """
      set bot defaults (such as personality fields) based on a configuration file
      """
      cfile = self.owner.config.get('Bot','defaults')
      cfg = ConfigParser()
      cfg.read(cfile)

      for name, value in cfg.items("personality"):
         self.k.setBotPredicate(name,value)

   def log(self, message):
      self.owner.log('aimbot',message)

   def saveSessions(self):
      """
      save all current sessions using marshal method.
      """
      session = self.k.getSessionData()
      sessionFile = file("all.ses", "wb")
      marshal.dump(session, sessionFile)
      sessionFile.close()

   def loadSessions(self):
      """
      load session data, such as conversation histories.
      """
      sessionFile = file("all.ses", "rb")
      sessions = marshal.load(sessionFile)
      sessionFile.close()
      for session in sessions.keys():
         for pred,value in sessions[session].items():
            self.k.setPredicate(pred, value, session)

   def on_IM_IN(self,data):
      in_sn, in_flag, in_msg = data.split(":")[0:3]
      msg = self.strip_html(in_msg)
      self.log(in_sn + ": " + msg)
      reply = self.makeReply(in_sn,msg)
      if reply:
         self.log("reply: " + reply)

         # split up replies that have two distinct thoughts in it, ie, send
         # more messages instead of all at once. (more human like, in my
         # opinion)
         for sentence in reply.split("\n\n"):
            self.sendReply(in_sn,sentence)

   def sendReply(self, sn, msg):
      """
      return an IM message with some text.

      this method is useful because it causes a bot reply to look more like a
      human reply. ie, it adds an artificial delay, changes emssage case, etc..
      """
      # make the response all lower case..
      msg = msg.lower()

      # pretend we are typing with an artificial timeout
      slept = 0
      for char in msg:
         time.sleep(self.typerate)
         slept += self.typerate
         if slept >= 5.0:
            break

      self.do_SEND_IM(sn,msg)

   def makeReply(self,sn,data):
      temp = 'unknown'
      freezer = 'unknown'
      if self.owner:
         temp = self.owner.last_temp
         freezer = self.owner.freezer.getStatus()
      response = self.k.respond(data,sn)

      return response

   def strip_html(self, text):
       """ from http://effbot.org/zone/re-sub.htm#strip-html """
       def fixup(m):
           text = m.group(0)
           if text[:1] == "<":
               return "" # ignore tags
           if text[:2] == "&#":
               try:
                   if text[:3] == "&#x":
                       return unichr(int(text[3:-1], 16))
                   else:
                       return unichr(int(text[2:-1]))
               except ValueError:
                   pass
           elif text[:1] == "&":
               import htmlentitydefs
               entity = htmlentitydefs.entitydefs.get(text[1:-1])
               if entity:
                   if entity[:2] == "&#":
                       try:
                           return unichr(int(entity[2:-1]))
                       except ValueError:
                           pass
                   else:
                       return unicode(entity, "iso-8859-1")
           return text # leave as is
       return re.sub("(?s)<[^>]*>|&#?\w+;", fixup, text)



