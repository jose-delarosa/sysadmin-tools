#!/bin/bash
set +x
# Create a VM from http, PXE or iso file. The VM is created on a storage
# pool, which must already exist and must be specified by the user.
#
# I don't create storage pools here because it's a fairly manual process, so
# all I do is list all existing storage pools. I do however, create storage
# volumes on the pools, except for iscsi, where it takes up the whole LUN.
#
# TODO: Ask if we want raw or qcow2 image

. /opt/dlr/misc/skel/colors
isodir=/share1/dell/isos
pooldir=/share1/images
pooldirname=dir

# My default storage pool names (very original)
defdirpool=dir			# this is what I use 99.95% of the time
deflvmpool=lvm
defpartpool=part
defiscsipool=iscsi
defnfspool=nfs

usage() {
   echo "Usage: `basename $0` <vm> <vcpu> <mem> <disk> <pxe|iso|os> [novnc]"
   echo "  mem is in GB"
   echo "  disk is in GB"
   echo "  os is r511|r66|r71|c66|c71|f22"
   exit
}

chkreqs() {
   [ -f /etc/redhat-release ] && vbin="libvirtd" || vbin="libvirt-bin"
   service $vbin status 1> /dev/null 2>&1
   if [ $? -ne 0 ] ; then
     echo "$vbin not installed or not running"
     exit 1
   fi

   # Exit if these binaries are not found, otherwise error is ugly
   bins="virsh brctl bc"
   for bin in $bins; do
      which $bin 1> /dev/null 2>&1
      if [ $? -eq 1 ] ; then
        echo "$bin not installed"
        exit 1
      fi
   done

   if [ $sel = "pxe" -a $disk -lt 8 ] ; then
      echo "With PXE, minimim disk size is 8 GB, as specified in ks file."
      exit 1
   fi

   if ! egrep -e 'vmx|svm' /proc/cpuinfo > /dev/null
   then
      echo "CPU does not support VT. OK to continue, but performance will lag."
   fi
}

chkbridge() {
   # If you find more than one bridge then give option of which to choose
   # Would be nice to also print network associated with it
   brlist=`brctl show | sed 1d | egrep '^[a-zA-Z]' | awk '{print $1}'`
   if [ X"$brlist" = X ] ; then
      echo "No bridge found! Aborting!"
      exit
   fi

   echo -e "${green}Network Bridges:${end}"
   cnt=1
   for br in $brlist; do
      echo " $cnt) $br"
      cnt=`expr $cnt + 1`
   done
   echo " q) quit"

   # select bridge
   brsel=
   while [ X"$brsel" = X ] ; do
      echo -n "select : "
      read brsel
   done

   [ $brsel = "q" ] && exit
   cnt=1
   for br in $brlist; do
      if [ $cnt -eq $brsel ] ; then
         brname=`echo $br`
         break
      fi
      cnt=`expr $cnt + 1`
   done

   if [ X"$brname" = X ] ; then
      echo "Invalid choice"
      exit
   fi
}

createpool() {
   virsh pool-define-as $pooldirname dir - - - - $pooldir
   virsh pool-build $pooldirname
   virsh pool-start $pooldirname 
   virsh pool-autostart $pooldirname 
   echo -e "${green}Created \"directory\" pool $pooldirname in $pooldir${end}"
}

dostorvol() {
   echo -e "${green}Storage Pools:${end}"
   pools=`virsh pool-list --details | sed '1,2d'`
   if [ X"$pools" = "X" ] ; then
      echo -e "${red}No storage pools found!${end}"
      echo -n "Create \"directory\" pool in $pooldir? [Y/n]: "
      read resp
      case $resp in
         n ) exit ;;
         * ) createpool ;;
      esac
   fi 

   echo "Select storage pool *type* to use:"
   echo " 1) Directory"
   echo " 2) LVM"
   echo " 3) Partition"
   echo " 4) NFS"
   echo " 5) iSCSI"
   echo -n "Select [1] : "
   read resp
   case $resp in
      2 ) storpool="lvm" ;;
      3 ) storpool="part" ;;
      4 ) storpool="nfs" ;;
      5 ) storpool="iscsi" ;;
      * ) storpool="dir" ;;
   esac

   if [ "$storpool" = "dir" ] ; then
      # Call a function here to create directory storage pool if it doesn't
      # already exist!
      #
      #
      #
      echo -n "Directory pool name [$defdirpool] : "
      read dirpool
      [ X"$dirpool" = X ] && dirpool=$defdirpool
      storpoolargs="vol=${dirpool}/${vm}"
      echo "Creating volume $vm in storage pool $dirpool..."
      virsh vol-create-as $dirpool $vm ${disk}G --format qcow2
      # could add "--format qcow2" but for now just using raw format
   elif [ "$storpool" = "lvm" ] ; then
      echo -n "LVM pool name [$deflvmpool] : "
      read lvmpool
      [ X"$lvmpool" = X ] && lvmpool=$deflvmpool
      storpoolargs="vol=${lvmpool}/${vm}"
      echo "Creating volume $vm in storage pool $lvmpool..."
      virsh vol-create-as $lvmpool $vm ${disk}G
   elif [ "$storpool" = "part" ] ; then
      echo -n "Partition pool name [$defpartpool] : "
      read partpool
      [ X"$partpool" = X ] && partpool=$defpartpool
      storpoolargs="vol=${partpool}/${vm}"
      echo "Creating volume $vm in storage pool $partpool..."
      virsh vol-create-as $partpool $vm ${disk}G
   elif [ "$storpool" = "nfs" ] ; then
      echo -n "NFS pool name [$defnfspool]: "
      read nfspool
      [ X"$nfspool" = X ] && nfspool=$defnfspool
      storpoolargs="vol=${nfspool}/${vm}"
      echo "Creating volume $vm in storage pool $nfspool..."
      virsh vol-create-as $nfspool $vm ${disk}G
   elif [ "$storpool" = "iscsi" ] ; then
      echo -n "iSCSI pool name [$defiscsipool]: "
      read iscsipool
      [ X"$iscsipool" = X ] && iscsipool=$defiscsipool
      iscsivol=`virsh vol-list $iscsipool | grep by-path | awk '{print $1}'`
      storpoolargs="vol=${iscsipool}/${iscsivol}"
      # No need to create volume, already exists!
   else
      echo "This storage pool is not yet supported"
      exit
   fi
}

dopxe() {
   virt-install --connect qemu:///system --network bridge:${brname} \
     --name ${vm} --ram=${mem} --vcpus=${vcpu} --disk ${storpoolargs} \
     --graphics ${graph} --pxe
}

donetwork() {
   if [ $sel = r511 ] ; then
      osdir="${osroot}/RedHat/RHEL5/5.11/Server/x86_64/os/"
      ks="ks=${osroot}/RedHat/RHEL5/5.11/Server/x86_64/ks-vm.cfg"
   elif [ $sel = r66 ] ; then
      osdir="${osroot}/RedHat/RHEL6/6.6/Server/x86_64/os"
      ks="ks=${osroot}/RedHat/RHEL6/6.6/ks-vm.cfg"
   elif [ $sel = r71 ] ; then
      osdir="${osroot}/RedHat/RHEL7/7.1/Server/x86_64/os"
      ks="ks=${osroot}/RedHat/RHEL7/7.1/ks-vm.cfg"
   elif [ $sel = c66 ] ; then
      osdir="${osroot}/centos/partners.centos.com/6.6/os/x86_64/"
      ks="ks=${osroot}/centos/ks-vm6.cfg"
   elif [ $sel = c71 ] ; then
      osdir="${osroot}/centos/partners.centos.com/7.1.1503/os/x86_64/"
      ks="ks=${osroot}/centos/ks-vm71.cfg"
   elif [ $sel = f22 ] ; then
      osdir="${osroot}/RedHat/fedora/linux/releases/22/Server/x86_64/os"
      ks="ks=${osroot}/RedHat/fedora/ks/ks-f22-vm.cfg"
   else
      echo "Invalid parameter. Now what do I do with storage volume?"
      return
   fi

   virt-install --connect qemu:///system --network bridge:${brname} \
     --name ${vm} --ram=${mem} --vcpus=${vcpu} --disk ${storpoolargs} \
     --graphics ${graph} --location="${osdir}" --extra-args="${ks} ${tty}"
}

doiso() {
   if [ ! -d $isodir ] ; then
      echo "$isodir does not exist, so no isos available to install from."
      exit
   fi
   echo "Available isos in $isodir:"
   isolist=`find $isodir -type f -exec basename '{}' \;`
   cnt=1
   for iso in $isolist ; do
      echo " $cnt) $iso"
      cnt=`expr $cnt + 1`
   done
   echo " q) quit"

   # input iso name
   isosel=
   while [ X"$isosel" = X ] ; do
      echo ; echo -n "select : "
      read isosel
   done

   [ $isosel = "q" ] && exit
   cnt=1
   for iso in $isolist ; do
      if [ $cnt -eq $isosel ] ; then
         isoname=`echo $iso`
         break
      fi 
      cnt=`expr $cnt + 1`
   done

   iso=`find $isodir -name $isoname`
   [ ! -f ${iso} ] && (echo "${iso} does not exist!" ; exit)

   virt-install --connect qemu:///system --network bridge:${brname} \
     --name ${vm} --ram=${mem} --vcpus=${vcpu} --disk ${storpoolargs} \
     --graphics ${graph} --cdrom=${iso}

     # Example of how to attach an iso during installation
     # --disk path=/share1/dell/isos/windows/virtio-win-0.1-81.iso,device=cdrom
}

# Process args
[ $# -lt 5 ] && usage
vm=$1
vcpu=$2
mem=$3
disk=$4
sel=$5

chkreqs					# check requirements
# If I have 6th arg, then VNC will NOT be used. I am not explicitly checking
# for the word "novnc", but who cares
[ $# -eq 6 ] && graph="none" || graph="vnc"

# Do we need to connect to the serial console?
[ "$graph" = "none" ] && tty="console=tty0 console=ttyS0,115200" || tty=

memf=`echo $mem \* 1024 | bc -l`	# convert memory from GB to MB
mem=${memf/.*}				# convert float to int
chkbridge				# check there's a bridge to use
dostorvol				# create storage volume

if [ `hostname -s` = "nuc" ] ; then
   osroot=http://nuc.dlr.com/pub/Distros
else
   osroot=http://geeko.linuxdev.us.dell.com/pub/Distros
fi

# Select installation method
if [ "$sel" = "iso" ] ; then
   doiso
elif [ "$sel" = "pxe" ] ; then
   dopxe
else
   donetwork
fi

# 2015.05.28 13:27:30 - JD
