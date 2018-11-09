#!/usr/bin/env python
#
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

# Examine directory and print info
# [dirname] [# of files] [# of dirs] [size]
# todo: how do I skip hard links?

import sys, os
ll = 80         		# line length to use

def usage(me):
   print "Usage: %s <options> <dir>" % me
   print "options:"
   print " -n | --nodetail  prints number of subdirs and files, and total size"
   print " -d | --detail    prints additional information about each subdirectory"
   print " -r | --raw       prints just total number of files"
   sys.exit(0)

def checkreqs(rootdir):
   if not os.path.isdir(rootdir):
      print "Not a directory!"
      print "Come on man, get with it."
      sys.exit(1)
   if rootdir == "/":
      # /dev and /proc are messy, so forbid it "/"
      print "'/' not allowed!"
      print "/dev and /proc are not standard file systems"
      sys.exit(1)
   if rootdir[-1:] == "/":
      # remove trailing slash if any
      rootdir = rootdir[0:-1]
   return rootdir

def printline(pattern):
   lin = ""
   for w in range(0, ll):
      lin = lin + pattern
   print lin
   return

def gettabs(rootdir):
   rdl = len(rootdir)
   if rdl < 8:    tabs = "\t\t\t\t\t\t"
   elif rdl < 16: tabs = "\t\t\t\t\t"
   elif rdl < 24: tabs = "\t\t\t\t"
   elif rdl < 32: tabs = "\t\t\t"
   elif rdl < 40: tabs = "\t\t"
   elif rdl < 48: tabs = "\t"
   else:          tabs = ""
   return tabs

def examinedir(rootdir, f):
   filcnt = 0
   dircnt = 0
   errcnt = 0
   fs = 0		# file size
   try:
      for root, dirs, files in os.walk(rootdir):
         for dir in dirs:
            dircnt += 1
         for file in files:
            fp = os.path.join(root, file)
            # do only if not a symlink; but what about hard links? :(
            if not os.path.islink(fp):
               filcnt += 1
               try:
                  fs += os.path.getsize(fp)
               except:
                  # print "Error: %s" % fp
                  errcnt += 1

   except KeyboardInterrupt:
      print "Aborted by user."
      sys.exit(1)

   if (f == "r"): return filcnt
   if fs < 1000:
      fsn = fs
      unit = "b"
   elif fs < 1000000:
      fsn = fs / 1024.0
      unit = "kb"
   elif fs < 1000000000:
      fsn = fs / 1024.0 / 1024.0
      unit = "mb"
   else:
      fsn = fs / 1024.0 / 1024.0 / 1024.0
      unit = "gb"

   dir = os.path.basename(rootdir)
   tabs = gettabs(dir)
   print "%s%s%s\t%s\t%.2f %s" % (dir, tabs, dircnt, filcnt, fsn, unit)
   if errcnt > 0: print "* Could not get information for %s files" % errcnt

def main():
   if len(sys.argv) < 3:
      usage(sys.argv[0])

   f = sys.argv[1][1:]
   if not (f == "n" or f == "d" or f == "r"):
      usage(sys.argv[0])
   rootdir = checkreqs(sys.argv[2])

   if (f == "n" or f == "d"):
     print "Directory\t\t\t\t\tSubDirs\tFiles\tSize"
     printline("-")
   
   if f == "n":
      examinedir(rootdir, f)
   elif f == "d":
      for item in sorted(os.listdir(rootdir)):
         if os.path.isdir(rootdir + "/" + item):
            examinedir(rootdir + "/" + item, f)
   else:
      print examinedir(rootdir, f)

if __name__ == "__main__":
   main()

# 2015.07.06 22:28:56 - JD
