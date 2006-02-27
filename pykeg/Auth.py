import thread
import time
import traceback

import Backend

class AbstractMethodError(Exception):
   pass


class GenericIBAuth:
   def __init__(self, owner, device, refresh_timeout, quit_event, logger):
      self.owner = owner
      self.device = device
      self.refresh_timeout = refresh_timeout
      self.QUIT = quit_event
      self.logger = logger

      self.ibs = []
      self._allibs = {}

   def _UpdateState(self, ibs):
      """ Record IB event histories """
      # mark presence bit for new ibs
      for ibid in ibs:
         if not self._allibs.has_key(ibid):
            self._allibs[ibid] = [0] * 6
         self._allibs[ibid] = [1] + self._allibs[ibid][:5]

      # mark absence bit for recent ibs
      for ibid in [x for x in self._allibs.keys() if x not in ibs]:
         self._allibs[ibid] = [0] + self._allibs[ibid][:5]

      # detect ib events
      for ibid, history in self._allibs.iteritems():
         if history == [0,0,0,1,1,1]:
            self._AbsenceEvent(ibid)
         elif history == [1,1,1,0,0,0]:
            self._PresenceEvent(ibid)

   def _AbsenceEvent(self, ibid):
      matches = Backend.Token.selectBy(keyinfo=ibid)
      if not matches.count():
         return
      user = Backend.User.get(matches[0].userid)
      if not user:
         return
      self.logger.info('key %s user %s is gone' % (ibid, user.username))
      self.owner.deauthUser(user.username)

   def _PresenceEvent(self, ibid):
      matches = Backend.Token.selectBy(keyinfo=ibid)
      if not matches.count():
         return
      user = Backend.User.get(matches[0].userid)
      self.logger.info('key %s belongs to user %s' % (ibid, user.username))
      self.owner.authUser(user.username)

   def _RefreshLoop(self):
      """ Periodically update self.ibs with the current ibutton list. """
      while not self.QUIT.isSet():
         self._UpdateState(self._GetPresentIDs())
         time.sleep(self.refresh_timeout)
      self.logger.info('quit')

   def start(self):
      try:
         self._Bootstrap()
         thread.start_new_thread(self._RefreshLoop, ())
      except:
         self.logger.error('error connecting to onewirenet')
         traceback.print_exc()

   def _GetPresentIDs(self):
      raise AbstractMethodError

   def _Bootstrap(self):
      raise AbstractMethodError


class SerialIBAuth(GenericIBAuth):
   """ iButton auth class for a serial DSXXXX reader """
   def _Bootstrap(self):
      import onewirenet
      self.ownet = onewirenet.onewirenet(self.device)
      self.logger.info('new onewire net at device %s' % self.device)
      return True

   def _GetPresentIDs(self):
      return [ib.read_id() for ib in self.ownet.refresh()]


class USBIBAuth(GenericIBAuth):
   """ iButton auth class for a USB DS2490 reader """
   def _Bootstrap(self):
      import usb
      usb.UpdateLists()
      import ds2490
      try:
         self.ownet = ds2490.DS2490()
      except ValueError:
         self.logger.error('ds2490 not connected; disabled')
         return False
      return True

   def _GetPresentIDs(self):
      return map(str, self.ownet.GetIDs())


