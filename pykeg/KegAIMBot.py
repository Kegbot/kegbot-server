from toc import TocTalk, BotManager

class KegAIMBot(TocTalk):
   def __init__(self, sn, pw, owner):
      TocTalk.__init__(self,sn,pw)
      self.owner = owner
      self._info = "hello, i am a kegerator."
      self._debug = 1 # critical debug messages
      self._logfd = open('botlog.txt','a',0)

   def on_IM_IN(self,data):
      in_sn, in_flag, in_msg = data.split(":")[0:3]
      reply = self.makeReply(in_msg)
      if reply:
         self.do_SEND_IM(in_sn,reply)

   def makeReply(self,data):
      temp = 'unknown'
      freezer = 'unknown'
      if self.owner:
         temp = self.owner.last_temp
         freezer = self.owner.freezer.getStatus()
      reply = "i am dumb. my last recorded temperature is %s and the freezer is believed to be %s." % (temp,freezer)
      return reply


