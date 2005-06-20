import select
import time
import struct

fifo = '/tmp/flow.fifo'
fp = open(fifo, 'r+')

c = 0
while 1:
   c += 10
   high = c/256
   low  = c%256
   fp.write('M:' + struct.pack('BBBBB', 1,0,1,high,low) + '\r\n')
   fp.flush()
   time.sleep(1.0)

