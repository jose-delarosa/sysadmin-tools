#!/usr/bin/env python
# Copyright 2018 Jose Delarosa
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# This script will get a specific URL and either return basic information
# about the site or will throw out an error that URL does not exist.
# Seems to work even when using a proxy server, but it times out on some
# sites, not sure why.

import sys, os, urllib2
from urllib2 import Request, urlopen, URLError

def usage(me):
   print "Usage: %s <url>" % (me)
   exit(0)

# some sanity checking
def verifyurl(url):
   str1 = "http://"                      # http protocol
   str2 = "https://"                     # https protocol
   if not url.startswith(str1) and not url.startswith(str2):
      print "URL does not start with \"%s\" or \"%s\"" % (str1, str2)
      sys.exit(1)
   return

def getresp(url):
   try:
      response = urllib2.urlopen(url)
   except URLError, e:
      if hasattr(e, 'reason'):
         print "Couldn't connect to server. Reason:", e.reason
         sys.exit(1)
      elif hasattr(e, 'code'):
         print 'The server couldn\'t fulfill request. Code: ', e.code
         sys.exit(1)
   except KeyboardInterrupt:	# let's add this for when it hangs
      print "Aborted by user."
      sys.exit(1)
   return response

def printinfo(resp):
   print "URL: ", resp.geturl()		# Get the URL
   print "Return code: ", resp.code	# Get the code
 
   # Get the Headers. This returns a dictionary-like object that describes the
   # page fetched, particularly the headers sent by the server
   print "Headers: ", resp.info()
   print "Date: ", resp.info()['date']     # Get the date part of the header
   print "Server: ", resp.info()['server'] # Get the server part of the header
   html = resp.read()
   #print "Data: ", html		# Get all data - lots of stuff
   print "Length :", len(html)		# Get only the length
 
   # Show that the file object is iterable; rstrip strips the trailing
   # newlines and carriage returns before printing the output.
   for line in resp:
      print line.rstrip()
   return

def main():
   if len(sys.argv) < 2:	# Check args
      usage(sys.argv[0])
   url = sys.argv[1]
   verifyurl(url)
   resp = getresp(url)          # get 'response' from URL
   printinfo(resp)

if __name__ == "__main__":
   main()

# 2013.11.06 13:55:28 - JD
