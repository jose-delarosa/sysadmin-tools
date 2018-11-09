#!/bin/bash
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

# Scan network for hosts
network=

# Exit if nmap not found, because regular error is ugly
x=`which nmap 1> /dev/null 2>&1`
if [ $? -eq 1 ] ; then
   echo "nmap not installed"
   exit 1
fi

# Find available networks
netlist=`ip addr show | grep inet | awk '{print $2}' | egrep -v ^'fe80|127.0|::|fd0c'`
cnt=1
echo "Available networks:" ; echo
echo " 0) quit"
for net in $netlist; do
   echo " $cnt) $net"
   cnt=`expr $cnt + 1`
done
echo

# select network to scan
netsel=
while [ X"$netsel" = X ] ; do
   echo -n "select : "
   read netsel
done

if [ $netsel -eq 0 ] ; then
   exit 1
fi
cnt=1
for net in $netlist ; do
   if [ $cnt -eq $netsel ] ; then
      network=`echo $net`
      break
   fi
   cnt=`expr $cnt + 1`
done

echo "Scanning $network (one moment please)..." ; echo
network_s=`echo $network | awk -F "." '{print $1"."$2}'`
nmap -sP ${network} | grep ${network_s} | awk -F " " '{print $5 $6}'

# 2013.03.27 11:04:42 - JD
