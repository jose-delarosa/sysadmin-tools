#!/usr/bin/env python
#
# +-------+----------+-----+------+-------------+-------------+
# | name  | state    | cpu | ram  | disk        | ip          |
# +-------+----------+-----+------+-------------+-------------+
# | cent7 | running  | 1   | 1024 | 25 GB (52%) | 192.168.0.3 |
# | juno  | shut off | 2   | 4096 | 40 GB (41%) | n/a         |
# | named | shut off | 1   | 512  | 4 GB (57%)  | n/a         |
# +-------+----------+-----+------+-------------+-------------+

import sys, os, subprocess
from subprocess import Popen, PIPE, STDOUT

sdir = "/opt/dlr"
execfile(sdir + "/misc/skel/colors")

# this simple list specifies order to print the columns
list = ["name", "state", "cpu", "ram", "disk", "ip"]
list_prnt = ["name", "state", "cpu", "ram", "disk", "ip"]
col = {}
for l in list: col[l] = len(l)		# minimum column width

def die(msg):
   print >>sys.stderr, msg
   os._exit(1)

def checkreqs():
   # do binaries exist?
   bins = ['bc', 'virsh', 'brctl']
   for b in bins:
      if which(b) == None:
         print "%s not found!" % b
         return False

   # is libvirtd running?
   try:
      if os.path.isfile("/etc/redhat-release"): vbin = "libvirtd"
      else: vbin = "libvirt-bin" 
      s = "service %s status 1> /dev/null 2>&1" % vbin
      result = subprocess.call(s, shell=True)
   except KeyboardInterrupt:
      die("Interrupt detected, exiting.")
   except:
      raise
   if not result == 0:
      die("libvirtd not installed or not running.")

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

def getvms():
   vmnames = []
   s = 'virsh list --all'
   try:
      p = Popen(s, shell=True, stdout=PIPE, stderr=STDOUT)
      out = p.stdout.read().rstrip().lstrip()	# remove EOL and left spaces
   except KeyboardInterrupt:
      die("Interrupt detected, exiting.")
   except: raise

   for line in out.split("\n")[2:]:		# skip first 2 lines
      vm = line.split()[1]
      vmnames.append(vm)			# build out array

   if not vmnames:
      print "No VMs on this host! How about creating one first?"
      sys.exit(0)

   maxvmlen = len(max(vmnames, key=len))        # get max length
   if maxvmlen > col["name"]: col["name"] = maxvmlen
   return vmnames

def getstate(vm):
   s = 'virsh dominfo %s' % vm["name"]
   try:
      p = Popen(s, shell=True, stdout=PIPE, stderr=STDOUT)
      out, err = p.communicate()
   except KeyboardInterrupt:
      die("Interrupt detected, exiting.")
   except: raise

   for line in out.split("\n"):
      if "State" in line.split(":")[0]:
         st = line.split(":")[1].rstrip().lstrip() 
         vm["state"] = st
         if len(st) > col["state"]: col["state"] = len(st)
      if "CPU(s)" in line.split(":")[0]:
         cpu = line.split(":")[1].rstrip().lstrip() 
         vm["cpu"] = cpu
         if len(cpu) > col["cpu"]: col["cpu"] = len(cpu)
      if "Used memory" in line.split(":")[0]:
         ram = line.split(":")[1].rstrip().lstrip() 
         ram = float(ram.split(" ")[0]) / 1024	# convert so I can divide
         ram = int(ram)				# take "." away
         vm["ram"] = ram
         if len(str(ram)) > col["ram"]: col["ram"] = len(str(ram))
   return vm

def getdisk(vm):
   # query the pool volume
   s = 'virsh vol-info --pool dir %s' % vm["name"]
   try:
      p = Popen(s, shell=True, stdout=PIPE, stderr=STDOUT)
      out, err = p.communicate()
   except KeyboardInterrupt:
      die("Interrupt detected, exiting.")
   except: raise

   if "error" in out:		# some VMs may not have a volume :(
      vm["disk"] = "n/a"
      return vm

   da = 0
   dc = 0
   for line in out.split("\n"):
      if "Capacity" in line.split(":")[0]:
         dc = line.split(":")[1].rstrip().lstrip()
         dc = dc.split(" ")[0]
      if "Allocation" in line.split(":")[0]:
         da = line.split(":")[1].rstrip().lstrip()
         da = da.split(" ")[0]

   if not da == 0 and not dc == 0:		# always check
      pe = " ({0:.0%})".format(float(da) / float(dc))	# WTF?
      dc = dc.split(".")[0] + " GB"		# take "." away
      vm["disk"] = dc + pe			# these are strings!
      if len(dc + pe) > col["disk"]: col["disk"] = len(dc + pe)
   else:
      vm["disk"] = "n/a"
   return vm

def getip(vm):
   ip = ""
   # get mac address of VM
   s = 'virsh dumpxml %s | grep "mac address"' % vm["name"]
   try:
      p = Popen(s, shell=True, stdout=PIPE, stderr=STDOUT)
      out = p.stdout.read().rstrip().lstrip()
   except KeyboardInterrupt:
      die("Interrupt detected, exiting.")
   except: raise

   if not out:				# no mac address?
      vm.append("n/a")
      return vm

   # <mac address='52:54:00:c5:8f:3f'/>  --> 52:54:00:c5:8f:3f
   mac = out.split("=")[1].split("/")[0][:-1][1:]

   # query ARP table and match MAC address found above
   s = 'ip neigh | grep %s' % mac
   try:
      p = Popen(s, shell=True, stdout=PIPE, stderr=STDOUT)
      out = p.stdout.read().rstrip().lstrip()
   except KeyboardInterrupt:
      die("Interrupt detected, exiting.")
   except: raise

   if not out:				# unlikely, but catch it
      vm["ip"] = "n/a"
      if len(vm["ip"]) > col["ip"]: col["ip"] = len(vm["ip"])
      return vm

   for line in out.split("\n"):
      ip = ip + " " + line.split(" ")[0]
   vm["ip"] = ip.lstrip()
   if len(ip.lstrip()) > col["ip"]: col["ip"] = len(ip.lstrip())
   return vm

def printheader():
   line = "+"
   for a in list_prnt:			# go through vm properties
      for x in range(0, col[a]+2): line = line + "-"
      line = line + "+"
   return line

def printtitle():
   t = ""
   for a in list_prnt:			# go through vm properties
      s = "| " + bold + a + end
      l = col[a]+3 - len("| " + a)
      for x in range(0, l):
         s = s + " "
      t = t + s				# total line 
   t = t + "|"				# ending '|'
   print t
   return

def printvminfo(b):
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
      t = t + s                         # total line
   t = t + "|"                          # ending '|'
   print t
   return

def main():
   vmall = []
   if checkreqs() == False:
      print red + "System check failed, please correct and try again." + end
      sys.exit(1)

   for vmname in getvms():
      vm = {}
      vm["name"] = vmname
      vm = getdisk(vm)
      vm = getip(vm)
      vm = getstate(vm)
      vmall.append(vm)
   line = printheader()
   print line
   printtitle()
   print line
   for vm in vmall:
      printvminfo(vm)
   print line

if __name__ == "__main__":
   main()

# 2015.07.29 12:06:46 - JD
