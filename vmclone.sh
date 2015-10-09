#!/bin/bash
# Clone a VM

usage() {
   echo "Usage: `basename $0` <template> <newvm>"
   exit
}

# Process args
[ $# -lt 2 ] && usage
template=$1
newvm=$2

[ -f /etc/redhat-release ] && vbin="libvirtd" || vbin="libvirt-bin"
service $vbin status 1> /dev/null 2>&1
if [ $? -ne 0 ] ; then
  echo "$vbin not installed or not running"
  exit 1
fi

# Exit if virt-clone not found, because regular error is ugly
which virt-clone 1> /dev/null 2>&1
if [ $? -eq 1 ] ; then
  echo "virt-clone not installed"
  exit 1
fi

echo "Cloning from $template to $newvm...just a moment please..."
virt-clone --connect qemu:///system --original ${template} --name ${newvm} --file /share3/img/${newvm}

# 2015.08.03 22:56:50 - JD
