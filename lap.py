#!/usr/bin/env python
#
# Simple program that counts and displays the elapsed number of seconds.
# It can either count from 1 to infinity or count the seconds of a
# minute (note that eventually timer will lag real-time clock) 

import sys, time
flag = 0

if len(sys.argv) == 2 and sys.argv[1] == 'real':
   # count from 1 to 60 and repeat
   flag = 1
   now = time.localtime(time.time())
   count = int(float(time.strftime("%S", now)))
else:
   # start from 1
   count = 1

print "Elapsed time (Ctrl+C to stop)"
print
try:
   while True:
      sys.stdout.write(" %d \r" % (count))
      sys.stdout.flush()
      time.sleep(1)
      count += 1
      # Adjust when we hit 60
      if count == 60 and flag == 1:
         now = time.localtime(time.time())
         count = int(float(time.strftime("%S", now)))
except KeyboardInterrupt:
   print "Aborted by user."
   sys.exit(1)

# 2013.11.05 16:33:24 - JD
