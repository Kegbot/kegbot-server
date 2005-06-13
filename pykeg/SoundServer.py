import threading
import Queue
import os
import popen2

class SoundServer(threading.Thread):
   def __init__(self,owner,basedir):
      threading.Thread.__init__(self)
      self.owner = owner
      self.basedir = basedir
      self.log('basedir = %s' % self.basedir)
      self.events = Queue.Queue()

   def log(self,message):
      self.owner.info('soundserver',message)

   def run(self):
      self.log('server starting in blocking mode')
      while 1:
         e = self.events.get()
         try:
            etype, edata = e
         except:
            continue
         if etype == 'quit':
            self.log('server quitting')
            return
         if etype == 'play':
            soundfile = os.path.join(self.basedir,edata)
            self.play_now(soundfile)

   def play_now(self,file):
      self.log("playing file %s" % file)
      cmd = "wavplay %s" % file
      popen2.popen2(cmd)

   def quit(self):
      self.events.put_nowait(('quit',''))
