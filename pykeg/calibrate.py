from FlowController import *
def runTest(readings,method,pourvol):
   print "stating test: [%s,%s,%s]" % (method,readings,pourvol)

   x = FlowController("/dev/ttyS0")
   print ''
   print "press enter to open the solenoid and begin the test.",
   raw_input()
   print ''

   rdata = []
   roz = []
   for i in range(readings):
      # begin reading i
      rd_ticks = 0
      last_ticks = 0
      x.clearTicks()
      time.sleep(0.1)
      last_read = 0
      while 1:
         print "begin: reading number %s ..." %(i,)
         curr = x.readTicks()
         new = curr - last_ticks
         rd_ticks += new
         if new > 1:
            last_read = time.time()
         if rd_ticks > 10 and time.time()-last_read > 4:
            print "end: last change in ticks was more than 4 seconds ago"
            break
         print " + %s = %s" %(new,rd_ticks)
         time.sleep(1.0)
      print "reading %s ended" % (i,)
      print "total ticks: %s" % rd_ticks
      rdata.append(rd_ticks)
      if method == 'manual':
         oz = raw_input('ounces in that pour? ')
         roz.append(float(oz))
      else:
         roz.append(pourvol)
      print "----------------------------------------"

   # now, compute the readings
   avg_ounces = 0
   avg_ticks = 0

   for vol in roz:
      avg_ounces += vol
   avg_ounces = avg_ounces/len(roz)

   for tick in rdata:
      avg_ticks += tick
   avg_ticks = avg_ticks/len(rdata)

   print "averages"
   print "---------------------"
   print "ticks:\t%s" % avg_ticks
   print "ounces:\t%s" % (avg_ounces,)
   print ""
   print " = %s ticks/oz" % (float(avg_ticks)/avg_ounces)
   print ""


print "flowmeter calibration. press return to continue...",
raw_input('')
print ''
print "first, we want to know how amny readings you want to take."
print "the more readings you take, the better i can guess the the"
print "calibration."
print ''
readings = raw_input("number of readings? [3] ")
if readings == '':
   readings = 3
try:
   readings = float(readings)
except:
   readings = 3
print ''
print "next, you have to tell me how many ounces will be in each"
print "reading. there are two methods available: static, and manual."
print ''
print "  - if you select static, i will ask you for a volume and i"
print "    will assume that is how much you poured, for each reading."
print "  - if you select manual, i will prompt you for the amount"
print "    you poured after each measurement"
print ''
method = raw_input("pour volume method? [STATIC/manual] ")
if method == '':
   method = 'static'
print ''
if method.lower() == 'static':
   print "you have selected a fixed volume for each pour. please enter the"
   print "number of ounces you expect to pour per each measurement"
   pourvol  = raw_input("ounces expected per pour? [12.0] ")
   try:
      pourvol = float(pourvol)
   except:
      pourvol = 12.0
elif method.lower() == 'manual':
   print "you have selected manual entry. i'll prompt you (when i detect the"
   print "pour is over) to type the amount you poured."
print ''
print "configuration complete. here is how i will set up the calibration:"
print ''
print "\treadings:\t%s" % readings
print "\tmethod:  \t%s" % method
if method.lower() == 'static':
   print "\tpourvol:\t%s" % pourvol
print ''
