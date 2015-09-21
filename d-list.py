#!/usr/bin/env python
#
# Print container information in a nice format, using mostly 'docker inspect'.
#
# +----------+---------+--------------+-------------+
# | name     | state   | image        | ip          |
# +----------+---------+--------------+-------------+
# | registry | running | registry:2.0 | 172.17.0.12 |
# | smb      | running | samba        | 172.17.0.7  |
# | httpd1   | running | httpd-home   | 172.17.0.2  |
# +----------+---------+--------------+-------------+

import sys, os, subprocess
from subprocess import Popen, PIPE, STDOUT
from optparse import OptionParser

# colors
red="\033[91m"
green="\033[92m"
bold="\033[1m"
end="\033[0m"

# this list specifies order to print columns
list = ["name", "id", "state", "cmd", "pid", "ip", "port", "vols", "image", "node"]
list_prnt = ["name", "state", "image", "ip"]		# default items to print
col = {}
for l in list: col[l] = len(l)		# minimum column width

def die(msg):
   print >>sys.stderr, msg
   os._exit(1)

def usage(me):
   print "Usage: %s [-P] [-v] [-n] [-c] [-p]" % me
   print "Use -h or --help for additional information."
   return

def checkreqs():
   # do binaries exist?
   bins = ['docker']
   for b in bins:
      if which(b) == None:
         print "%s not found!" % b
         return False

   # is docker running?
   try:
      s = 'service docker status 1> /dev/null 2>&1'
      result = subprocess.call(s, shell=True)
   except KeyboardInterrupt:
      die("Interrupt detected, exiting")
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

def getcontainers():
   coids = []
   s = 'docker ps -a'
   try:
      p = Popen(s, shell=True, stdout=PIPE, stderr=STDOUT)
      out = p.stdout.read().rstrip().lstrip()	# remove EOL and left spaces
   except KeyboardInterrupt:
      die("Interrupt detected, exiting.")
   except: raise

   for line in out.split("\n")[1:]:		# skip first line
      co = line.split()[0]
      coids.append(co)                          # build out array

   if not coids:
      print "No containers on this host yet."
      sys.exit(0)

   col["id"] = len(max(coids, key=len))	        # get max length
   return coids

def getstate(co):
   s = "docker inspect -f \'{{.State.Pid}}\' %s" % co["id"]
   try:
      p = Popen(s, shell=True, stdout=PIPE, stderr=STDOUT)
      pid = p.stdout.read().rstrip().lstrip()
   except KeyboardInterrupt:
      die("Interrupt detected, exiting")
   except: raise

   co["pid"] = pid
   if len(pid) > col["pid"]: col["pid"] = len(pid)

   if pid == "0": co["state"] = "shut off"
   else: co["state"] = "running"
   if len(co["state"]) > col["state"]: col["state"] = len(co["state"])
   return co

def getname(co):
   s = "docker inspect -f \'{{.Name}}\' %s" % co["id"]
   try:
      p = Popen(s, shell=True, stdout=PIPE, stderr=STDOUT)
      name = p.stdout.read().strip().split("/")[1]
   except KeyboardInterrupt:
      die("Interrupt detected, exiting")
   except: raise

   co["name"] = name
   if len(name) > col["name"]: col["name"] = len(name)
   return co

def getimage(co):
   s = "docker inspect -f \'{{.Config.Image}}\' %s" % co["id"]
   try:
      p = Popen(s, shell=True, stdout=PIPE, stderr=STDOUT)
      image = p.stdout.read().strip()
   except KeyboardInterrupt:
      die("Interrupt detected, exiting")
   except: raise

   co["image"] = image
   if len(image) > col["image"]: col["image"] = len(image)
   return co

def getcmd(co):
   s = "docker inspect -f \'{{.Config.Cmd}}\' %s" % co["id"]
   try:
      p = Popen(s, shell=True, stdout=PIPE, stderr=STDOUT)
      cmd = p.stdout.read().strip()[1:][:-1]
   except KeyboardInterrupt:
      die("Interrupt detected, exiting")
   except: raise

   if cmd == "no value":
      s = "docker inspect -f \'{{.Config.Entrypoint}}\' %s" % co["id"]
      try:
         p = Popen(s, shell=True, stdout=PIPE, stderr=STDOUT)
         cmd = p.stdout.read().strip()[1:][:-1]
      except KeyboardInterrupt:
         die("Interrupt detected, exiting")
      except: raise

   co["cmd"] = cmd
   if len(cmd) > col["cmd"]: col["cmd"] = len(cmd)
   return co

def getip(co):
   s = "docker inspect -f \'{{.NetworkSettings.IPAddress}}\' %s" % co["id"]
   try:
      p = Popen(s, shell=True, stdout=PIPE, stderr=STDOUT)
      ip = p.stdout.read().strip()
   except KeyboardInterrupt:
      die("Interrupt detected, exiting")
   except: raise

   if not ip: ip = "n/a"
   co["ip"] = ip
   if len(ip) > col["ip"]: col["ip"] = len(ip)
   return co

def getports(co):
   # Get port inside the container
   s1 = ' '.join(["docker inspect -f",
       "\'{{range $p, $conf := .NetworkSettings.Ports}} {{$p}}",
       "{{end}}\' %s" % co["id"]])
   # Get port mapped in the host
   s2 = ' '.join(["docker inspect -f",
       "\'{{range $conf := .NetworkSettings.Ports}}",
       "{{(index $conf 0).HostPort}} {{end}}\' %s" % co["id"]])
   try:
      ret = Popen(s1, shell=True, stdout=PIPE, stderr=STDOUT)
      p1 = ret.stdout.read().strip()
      data = ret.communicate()[0]
      if ret.returncode == 1: p1 = "n/a"	# capture errors
      if not p1: p1 = "n/a"			# no error, but could be blank

      ret = Popen(s2, shell=True, stdout=PIPE, stderr=STDOUT)
      p2 = ret.stdout.read().strip()
      # If the port in the container is not mapped to a port in the host then
      # I get this long ugly error message, so checking returncode which is set
      # to 1 if a port it's not mapped to the host
      data = ret.communicate()[0]
      if ret.returncode == 1: p2 = "n/a"
      if not p2: p1 = "n/a"			# no error, but could be blank

   except KeyboardInterrupt:
      die("Interrupt detected, exiting")
   except: raise

   port = p1 + " -> " + p2
   co["port"] = port
   if len(port) > col["port"]: col["port"] = len(port)
   return co

def getvols(co):
   s = "docker inspect -f \'{{.HostConfig.Binds}}\' %s" % co["id"]
   try:
      ret = Popen(s, shell=True, stdout=PIPE, stderr=STDOUT)
      vols = ret.stdout.read().strip().lstrip('[').rstrip(']')
      data = ret.communicate()[0]
      if ret.returncode == 1: node = "error"	# capture errors
      if not vols: vols = "none"
      if vols == "<no value>": vols = "none"
   except KeyboardInterrupt:
      die("Interrupt detected, exiting")
   except: raise

   co["vols"] = vols
   if len(vols) > col["vols"]: col["vols"] = len(vols)
   return co

def getnodes(co):
   s = "docker inspect -f \'{{.Node.Name}}\' %s" % co["id"]
   try:
      ret = Popen(s, shell=True, stdout=PIPE, stderr=STDOUT)
      node = ret.stdout.read().strip()
      data = ret.communicate()[0]
      if ret.returncode == 1: node = "error"	# capture errors
      if not node: node = "localhost"
      if node == "<no value>": node = "localhost"
   except KeyboardInterrupt:
      die("Interrupt detected, exiting")
   except: raise

   co["node"] = node
   if len(node) > col["node"]: col["node"] = len(node)
   return co

def printwhale():
   whale = """\
                               ##            .
                         ## ## ##           ==
                      ## ## ## ## ##       ===
                   /-------------------\___/ ===
              ~~~ {~~ ~~~~ ~~~ ~~ ~~~~ ~~ ~ /  === ~~~
                   \______ o             __/
                     \    \           __/
                      \____\_________/
   """ 
   print whale
   return

def printheader():
   line = "+"
   for a in list_prnt:			# go through properties
      for x in range(0, col[a]+2): line = line + "-"
      line = line + "+"
   return line

def printtitle():
   t = ""
   for a in list_prnt:			# go through properties
      s = "| " + bold + a + end
      l = col[a]+3 - len("| " + a)
      for x in range(0, l):
         s = s + " "
      t = t + s				# total line 
   t = t + "|"				# ending '|'
   print t
   return

def printcoinfo(b):
   t = ""
   for a in list_prnt:			# go through properties
      if str(a) == "state":
         if str(b[a]) == "running": s = "| " + green + str(b[a]) + end
         else: s = "| " + red + str(b[a]) + end
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
   coall = []
   if checkreqs() == False:
      print red + "System check failed, please correct and try again." + end
      sys.exit(1)

   # options parsing
   use = "Usage: %prog [options]\n\
   Display container information in a nice readable format."

   p = OptionParser(usage=use, description="")
   p.add_option('-P', action="store_true", dest="ports", help='ports', default=False)
   p.add_option('-v', action="store_true", dest="vols", help='volumes', default=False)
   p.add_option('-n', action="store_true", dest="node", help='node', default=False)
   p.add_option('-c', action="store_true", dest="cmd", help='command', default=False)
   p.add_option('-p', action="store_true", dest="pid", help='pid', default=False)
   (opts, args) = p.parse_args()
   error = False

   # Build out prnt_list
   # list = ["name", "id", "state", "cmd", "pid", "ip", "port", "vols", "image", "node"]
   if opts.ports == True: list_prnt.append("port")
   if opts.vols == True: list_prnt.append("vols")
   if opts.node == True: list_prnt.append("node")
   if opts.cmd == True: list_prnt.append("cmd")
   if opts.pid == True: list_prnt.append("pid")

   # Once you have built prnt_list, iterate through all found containers
   for coid in getcontainers():
      co = {}
      co["id"] = coid
      co = getstate(co)
      co = getname(co)
      co = getimage(co)
      co = getip(co)
      co = getcmd(co)
      co = getports(co)
      co = getnodes(co)
      co = getvols(co)
      coall.append(co)

   # printwhale()		# cute, but not needed
   line = printheader()
   print line
   printtitle()
   print line
   for co in coall:
      printcoinfo(co)
   print line

if __name__ == "__main__":
   main()

# 2015.08.19 20:49:38 - JD
