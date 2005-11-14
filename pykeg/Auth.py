import thread
import time
import traceback

import Backend

class SerialIBAuth:
   def __init__(self, owner, refresh_timeout, quit_event, logger):
      pass

   def start(self):
      pass

class USBIBAuth:
   def __init__(self, owner, refresh_timeout, quit_event, logger):
      self.owner = owner
      self.refresh_timeout = refresh_timeout
      self.QUIT = quit_event
      self.ibs = []
      self._allibs = {}
      self.logger = logger

   def start(self):
      try:
         import usb
         usb.UpdateLists()
         import ds2490
         try:
            self.dev = ds2490.DS2490()
         except ValueError:
            self.logger.error('ds2490 not connected; disabled')
            return
         thread.start_new_thread(self.RefreshLoop, ())
      except:
         self.logger.error('Error connecting to onewirenet')
         traceback.print_exc()

   def AbsenceEvent(self, ibid):
      matches = Backend.Token.selectBy(keyinfo=ibid)
      if not matches.count():
         return
      user = Backend.User.get(matches[0].id)
      if not user:
         return
      self.logger.info('key %s user %s is gone' % (ibid, user.username))
      self.owner.deauthUser(user.username)

   def PresenceEvent(self, ibid):
      matches = Backend.Token.selectBy(keyinfo=ibid)
      if not matches.count():
         return
      user = Backend.User.get(matches[0].id)
      self.logger.info('key %s belongs to user %s' % (ibid, user.username))
      self.owner.authUser(user.username)

   def RefreshLoop(self):
      """
      Periodically update self.ibs with the current ibutton list.

      Because there are at least two threads (temperature monitor, main event
      loop) that require fresh status of the onewirenetwork, it is useful to
      simply refresh them constantly.

      Note that the config file may specify IB IDs to ignore (such as the
      serial controller ID or other persistent IBs). These IDs will be sored in
      _allibs but not self.ibs, and that is the only difference.
      """
      while not self.QUIT.isSet():
         curribs = map(str, self.dev.GetIDs())

         # mark presence bit for new ibs
         for ibid in curribs:
            if not self._allibs.has_key(ibid):
               self._allibs[ibid] = [0] * 6
            self._allibs[ibid] = [1] + self._allibs[ibid][:5]

         # mark absence bit for recent ibs
         for ibid in [x for x in self._allibs.keys() if x not in curribs]:
            self._allibs[ibid] = [0] + self._allibs[ibid][:5]

         # detect ib events
         for ibid, history in self._allibs.iteritems():
            if history == [0,0,0,1,1,1]:
               self.AbsenceEvent(ibid)
            elif history == [1,1,1,0,0,0]:
               self.PresenceEvent(ibid)

         time.sleep(0.1)

      self.logger.info('quit')


