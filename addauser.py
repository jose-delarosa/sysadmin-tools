#!/usr/bin/env python
# Script to manually add users

import sys, os, subprocess, pwd, grp, getpass, time, shutil, re
from time import strftime

sdir = "/opt/dlr"
execfile(sdir + "/misc/skel/colors")
ll = 80                         # line length to use

# Users
min_uid = 1000
min_gid = 1000
pasfile = "/etc/passwd"
shafile = "/etc/shadow"
grpfile = "/etc/group"

def die(msg):
   print >>sys.stderr, msg
   os._exit(1)

def checkuser(name):
   try: return pwd.getpwnam(name)
   except KeyError: return None

def checkgroup(group):
   try: return grp.getgrnam(group)
   except KeyError: return None

def getfirst():
   fn = ""
   try:
      while len(fn) == 0: fn = raw_input('First Name: ')
   except KeyboardInterrupt: die("Interrupt detected, exiting.")
   return fn

def getlast():
   ln = ""
   try:
      while len(ln) == 0: ln = raw_input('Last Name: ')
   except KeyboardInterrupt: die("Interrupt detected, exiting.")
   return ln

def getusername(fn, ln):
   user = ""
   # Build username from first letter in 'fn' and up to 7 letters in 'ln'
   # Is this the best way to do it?
   fn1 = fn[0:1].lower()		# get first character
   ln = ln.replace(" ", "")		# remove empty spaces, if any
   ln7 = ln[0:7].lower()		# get first 7 characters
   user_rec = fn1 + ln7
   try:
      while len(user) == 0:
         user = raw_input('Username [' + green + '%s' % user_rec + end + ']: ')
         if len(user) == 0: user = user_rec
         if checkuser(user):
            print red + "Username %s already exists!" % user + end
            user = ""
   except KeyboardInterrupt: die("Interrupt detected, exiting.")
   return user

def getgroup(user):
   group = ""
   group_rec = user
   try:
      while len(group) == 0:
         group = raw_input('Group [' + green + '%s' % group_rec + end + ']: ')
         if len(group) == 0: group = group_rec
         if checkgroup(group):
            print red + "Group %s already exists!" % group + end
            group = ""
   except KeyboardInterrupt: die("Interrupt detected, exiting.")
   return group

def gethomedir(user):
   homedir = ""
   homedir_rec = "/home/" + user
   try:
      while len(homedir) == 0:
         homedir = raw_input('Home Dir [' + green+ '%s' % homedir_rec+end+']: ')
         if len(homedir) == 0: homedir = homedir_rec
         if os.path.exists(homedir):
            print red + "Directory %s already exists!" % homedir + end
            homedir = ""
   except KeyboardInterrupt: die("Interrupt detected, exiting.")
   return homedir

def getpasswd():
   passwd = ""
   passwdvfy = ""
   try:
      while True:
         while len(passwd) == 0: passwd = getpass.getpass()
         while len(passwdvfy) == 0:
            passwdvfy = getpass.getpass(prompt='Verify Password: ')
         if not passwd == passwdvfy:
            print red + "Password does not match!" + end
            passwd = ""
            passwdvfy = ""
         else: break
   except KeyboardInterrupt: die("Interrupt detected, exiting.")
   return passwd

def getuid(user):
   myuid = min_uid
   uid_list = []
   fh = open(pasfile, 'r')			# Read file
   ll = fh.readlines()
   fh.close()

   # read all lines in file, extract and sort
   for line in ll:
      uid = line.split(':')[2]  # Same as cut -d":" -f3
      uid_list.append(int(uid)) # Create array with uids (convert to int first)

   # Look for next available UID
   for uid in sorted(uid_list):
      if uid >= min_uid:
         if uid == myuid: myuid = myuid + 1
         else: break
   return myuid

def getgid(group):
   mygid = min_gid
   gid_list = []
   fh = open(grpfile, 'r')			# Read file
   ll = fh.readlines()
   fh.close()

   # read all lines in file, extract and sort
   for line in ll:
      gid = line.split(':')[2]  # Same as cut -d":" -f3
      gid_list.append(int(gid)) # Create array with gids (convert to int first)

   # Look for next available GID
   for gid in sorted(gid_list):
      if gid >= min_gid:
         if gid == mygid: mygid = mygid + 1
         else: break
   return mygid

def creategroup(group):
   # Get next available gid
   gid = getgid(group)
   s = "groupadd -g %s %s 1> /dev/null 2>&1" % (gid, group)
   result = subprocess.call(s, shell=True)
   # Failure?
   if not result == 0: print red + "Error in creating group %s" % group + end
   else: print green + "Created group %s" % group + end
   return result

def createuser(fn, ln, user, group, homedir):
   # Create backups
   ts = strftime("%Y.%m.%d %H:%M:%S")
   shutil.copy2(pasfile, pasfile + "." + ts)
   shutil.copy2(shafile, shafile + "." + ts)
   uid = getuid(user)
   s = ' '.join(["useradd -c \"%s %s\" -m -d %s " % (fn, ln, homedir),
             "-u %s -g %s %s 1> /dev/null 2>&1" % (uid, group, user)])
   result = subprocess.call(s, shell=True)
   # Failure?
   if not result == 0:
      print red + "Error in creating user %s" % user + end
      os.remove(pasfile + "." + ts)
      os.remove(shafile + "." + ts)
   else: print green + "Created user %s" % user + end
   return result

def setuserpass(user, passwd):
   # Set user password
   s = "echo %s | passwd --stdin %s 1> /dev/null 2>&1" % (passwd, user)
   result = subprocess.call(s, shell=True)
   if not result == 0: print red + "Error in setting password" + end
   else: print green + "Set password" + end
   return result

def main():
   # are we root
   if not os.geteuid() == 0:
      print "You must be root to run this script."
      sys.exit(1)

   print "Enter user information:\n"
   fn = getfirst()
   ln = getlast()
   user = getusername(fn, ln)
   passwd = getpasswd()
   group = getgroup(user)
   homedir = gethomedir(user)

   print " First name : %s" % fn
   print " Last name  : %s" % ln
   print " User       : %s" % user
   print " Password   : ********"
   print " Group      : %s" % group
   print " Home Dir   : %s" % homedir
   print "  c) continue"
   print "  q) quit"

   while True:
      choice = raw_input('Select [c] : ')
      if choice == "q":
         print "Nothing done"
         sys.exit(0)
      else: break

   if not creategroup(group) == 0: sys.exit(1)
   if not createuser(fn, ln, user, group, homedir) == 0:
      subprocess.call('groupdel %s 1> /dev/null 2>&1' % group, shell=True)
      sys.exit(1)		# remove group created
   setuserpass(user, passwd)

if __name__ == "__main__":
   main()

# 2015.02.21 14:48:03 - JD
