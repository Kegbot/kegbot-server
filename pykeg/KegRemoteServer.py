# the remote command server
import time
import threading
import SimpleXMLRPCServer
from KegRemoteFunctions import KegRemoteFunctions

class KegRemoteServer(threading.Thread):
   def __init__(self,kegbot,host,port):
      self.kegbot = kegbot
      self.host = host
      self.port = port
      self.QUIT = threading.Event()
      threading.Thread.__init__(self)

      # set up xml-rpc server
      self.functions = KegRemoteFunctions(kegbot,self)
      self.server = ReusableServer((host,port), logRequests = 0)
      self.server.register_instance(self.functions)

      # log the activation

   def run(self):
      while not self.QUIT.isSet():
         try:
            self.server.handle_request() # blocks; only way to get out is to call the quit function!
         except:
            print 'remote request handler got exception'
            raise
      self.server.server_close()
      time.sleep(0.1)

   def stop(self):
      self.QUIT.set()

class ReusableServer(SimpleXMLRPCServer.SimpleXMLRPCServer):
   """ an XMLRPC Server class that recovers nicely when previously terminated. """
   def server_bind(self):
      self.socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
      try:
         self.socket.bind(self.server_address)
      except: pass


