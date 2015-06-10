#!/usr/bin/env python
#
# +--------+---------+--------------+----------+----------------+
# | image  | tag     | id           | size     | created        |
# +--------+---------+--------------+----------+----------------+
# | omsa81 | centos7 | 44b61544c820 | 926.2 MB | 39 minutes ago |
# | omsa81 | centos6 | 443095b08939 | 963.5 MB | 54 minutes ago |
# | centos | centos6 | b9aeeaeb5e17 | 202.6 MB | 7 weeks ago    |
# | centos | centos7 | fd44297e2ddb | 215.7 MB | 7 weeks ago    |
# +--------+---------+--------------+----------+----------------+

import sys, os, subprocess
from subprocess import Popen, PIPE, STDOUT

sdir = "/opt/dlr"
# colors
red="\033[91m"
green="\033[92m"
bold="\033[1m"
end="\033[0m"

# this list specifies order to print columns
list = ["image", "tag", "id", "size", "created"]
list_prnt = ["image", "tag", "id", "size", "created"]
col = {}
for l in list:				# set minimum width to 3
   col[l] = 3

def die(msg):
   print >>sys.stderr, msg
   os._exit(1)

def checkreqs():
   # do binaries exist?
   bins = ['docker']
   for b in bins:
      if which(b) == None:
         print "'%s' not found!" % b
         return False
   try:
      s = 'service docker status 1> /dev/null 2>&1'
      result = subprocess.call(s, shell=True)
   except KeyboardInterrupt:
      die("Interrupt detected, exiting.")
   except:
      raise
   if not result == 0:
      die("docker not running or not installed!")
   return True

# Completely copied this function from the internet :(
def which(program):
   def is_exe(fpath):
      return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

   fpath, fname = os.path.split(program)
   if fpath:
      if is_exe(program): return program
   else:
      for path in os.environ["PATH"].split(os.pathsep):
         path = path.strip('"')
         exe_file = os.path.join(path, program)
         if is_exe(exe_file): return exe_file
   return None

def getim(im, line):
   im["image"] = line[0]
   if len(im["image"]) > col["image"]: col["image"] = len(im["image"])

   im["tag"] = line[1]
   if len(im["tag"]) > col["tag"]: col["tag"] = len(im["tag"])

   im["id"] = line[2]
   if len(im["id"]) > col["id"]: col["id"] = len(im["id"])

   im["size"] = line[6] + " " + line[7]
   if len(im["size"]) > col["size"]: col["size"] = len(im["size"])

   im["created"] = line[3] + " " + line[4] + " " + line[5]
   if len(im["created"]) > col["created"]: col["created"] = len(im["created"])
   return im

def printheader():
   line = "+"
   for a in list_prnt:			# go through container properties
      for x in range(0, col[a]+2): line = line + "-"
      line = line + "+"
   return line

def printtitle():
   t = ""
   for a in list_prnt:			# go through container properties
      s = "| " + bold + a + end
      l = col[a]+3 - len("| " + a)
      for x in range(0, l):
         s = s + " "
      t = t + s				# total line 
   t = t + "|"				# ending '|'
   print t
   return

def printiminfo(b):
   t = ""
   for a in list_prnt:			# go through properties
      if str(a) == "image":
         if "rhel" in str(b[a]): s = "| " + red + str(b[a]) + end
         elif "ubuntu" in str(b[a]): s = "| " + purple + str(b[a]) + end
         elif "suse" in str(b[a]): s = "| " + green + str(b[a]) + end
         else: s = "| " + str(b[a])
      else:
         s = "| " + str(b[a])
      l = col[a]+3 - len("| " + str(b[a]))
      for x in range(0, l):
         s = s + " "
      t = t + s				# total line 
   t = t + "|"				# ending '|'
   print t
   return

def main():
   imall = []
   if checkreqs() == False:
      print red + "System check failed, please correct and try again." + end
      sys.exit(1)

   s = "docker images"
   try:
      p = Popen(s, shell=True, stdout=PIPE, stderr=STDOUT)
      out = p.stdout.read().strip()
   except KeyboardInterrupt:
      die("Interrupt detected, exiting.")
   except: raise

   for line in out.split("\n")[1:]:             # skip first line
      im = {}
      im = getim(im, line.split())
      imall.append(im)

   if not imall:
      print "No container images on this host yet."
      sys.exit(0)

   line = printheader()
   print line
   printtitle()
   print line
   for im in imall:
      printiminfo(im)
   print line

if __name__ == "__main__":
   main()

# 2015.06.10 10:23:28 - JD
