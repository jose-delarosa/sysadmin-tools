#!/bin/bash
# Script to delete VMs to make my life easier

rmvm() {
   echo -n "Are you sure you want to delete $vm? [y/N] : "
   read resp
   case $resp in
      y ) echo "Removing $vm..." ;;
      * ) echo "Aborting." ; exit 1 ;;
   esac

   virsh destroy $vm 1> /dev/null 2>&1
   virsh undefine $vm
   virsh vol-delete --pool dir $vm
   echo "VM '$vm' deleted."
}

chkreqs() {
   [ -f /etc/redhat-release ] && vbin="libvirtd" || vbin="libvirt-bin"
   service $vbin status 1> /dev/null 2>&1
   if [ $? -ne 0 ] ; then
     echo "$vbin not installed or not running"
     exit 1
   fi

   # Exit if virsh not found, because regular error is ugly
   which virsh 1> /dev/null 2>&1
   if [ $? -eq 1 ] ; then
      echo "virsh not installed"
      exit 1
   fi
}

runthrough() {
   vm=$1
   vms=`virsh list --all | awk '{print $2}' | grep -v ^$`
   for v in $vms ; do
      [ $v = $vm ] && rmvm $vm      # Hit!
   done
}

if [ $# -lt 1 ] ; then
   echo "usage: `basename $0` <vm1> <vm2> ..."
   exit 1
fi

vmCnt=0
while [ $# -ge 1 ] ; do
   vmList[$vmCnt]=$1
   shift 1
   ((vmCnt++))
done

chkreqs
for vm in ${vmList[@]} ; do
   runthrough $vm
done

# 2015.10.09 14:04:38 - JD
