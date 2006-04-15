import xmlrpclib
import SimpleXMLRPCServer

"""
A simple client of kegbot events from Publisher.py.

You can subclass PykegClient, or run this script as a stand-alone module. Not
all event types are supported yet.
"""

class PykegClient:
   CLIENT_PASS = 0
   CLIENT_FAIL = 1
   CLIENT_HANGP = 2
   def KegbotEvent_Drink(self, id, kegid, userid, username, kegname,
         volume, endtime):
      print 'Got drink event: %(username)s had %(volume)i mL' % vars()
      return self.CLIENT_PASS

   def KegbotEvent_FlowStart(self, channel, userid, kegid, username, kegname):
      print 'Flow started for %(username)s on channel %(channel)s' % vars()
      return self.CLIENT_PASS

   def KegbotEvent_FlowEnd(self, channel, userid, kegid, username, kegname,
         volume):
      print 'Flow update: %(username)s %(volume)s mL' % vars()
      return self.CLIENT_PASS

   def KegbotEvent_PeriodicTemperature(self, temp):
      print 'Periodic temperature: %.2f' % temp
      return self.CLIENT_PASS

   def KegbotEvent_AlarmTemperature(self, temp):
      print 'Alarm Temperature: %.2f' % temp
      print 'You should probably do something about this!'
      return self.CLIENT_PASS


if __name__ == '__main__':
   client_obj = PykegClient()
   server = SimpleXMLRPCServer.SimpleXMLRPCServer(('', 9091))
   server.register_instance(client_obj)
   server.register_introspection_functions()

   server.serve_forever()
