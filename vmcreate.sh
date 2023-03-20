#!/bin/bash
#
# Create a VM via pxe, iso or network location. The VM is created in a local
# directory storage pool.
#
# TODO: - ask if we want raw or qcow2 image
#       - should I use file extension .qcow2?
#       - clean up printing storage volume
#       - output space left in storage volume selected

. $COLORFILE
iso_loc=/share3/isos
supported_distros="r90 r86 c84 f36"
def_dist=f36
def_pool=default

# options to set
vm=
vcpu=
ram=
disk=
pool=
osvariant=
install=
distro=$def_dist
vnc=yes
bridge=
mac=

usage() {
    echo "Usage: `basename $0` <options>"
    echo "Options:"
    echo "  -n --name <vm>         VM name"
    echo "  -v --vcpu <vcpus>      vCPUs"
    echo "  -r --ram <ram>         RAM amount (GB)"
    echo "  -s --disk <size>       Disk size (GB)"
    echo "  -o --osvariant <size>  OS variant (rhel9.x, fedora31, ubuntu22.04)"
    echo "  -p --pool <name>       Storage pool (def: \"$def_pool\")"
    echo "  -i --install <type>    Choices: pxe, iso, net"
    echo "  -d --distro <distro>   Used if install=net (def: \"$def_dist\")"
    echo "                         Choices: $supported_distros"
    echo "  -g --vnc <yes|no>      Use VNC (def: \"$vnc\")"
    echo "  -b --bridge <bridge>   Network bridge (optional)"
    echo "  -m --mac <address>     VM MAC address (optional)"
    echo "  -h --help              Display this menu"
    exit
}

check_requirements() {
    [ -f /etc/redhat-release ] && vbin="libvirtd"
    systemctl status $vbin 1> /dev/null 2>&1
    if [ $? -ne 0 ] ; then
        echo "$vbin not installed or not running"
        exit 1
    fi

    # Exit if these binaries are not found, otherwise error is ugly
    bins="virsh bc"
    for bin in $bins; do
        which $bin 1> /dev/null 2>&1
        if [ $? -eq 1 ] ; then
            echo "$bin not installed"
            exit 1
        fi
    done

    if [ $install = "pxe" -a $disk -lt 8 ] ; then
        echo "With PXE, minimim disk size is 8 GB, as specified in ks file."
        exit 1
    fi

    if ! egrep -e 'vmx|svm' /proc/cpuinfo > /dev/null
    then
        echo "CPU does not support VT. Performance will not be optimal."
    fi
}

setup_bridge() {
    # If you find more than one bridge then give option which to choose
    # (old way using brctl which is looks to be deprecated in RHEL 8)
    # brlist=`brctl show | sed 1d | egrep '^[a-zA-Z]' | awk '{print $1}'`

    # nmcli is not installed in Ubuntu by default so think about switching
    brlist=`brctl show | sed 1d | egrep '^[a-zA-Z]' | awk '{print $1}'`
    #brlist=`nmcli connection show --active | grep -w bridge | awk '{print $1}'`
    if [ X"$brlist" = X ] ; then
        echo "No bridge found! Aborting!"
        exit
    fi

    echo -e "${green}Select a network bridge:${end}"
    cnt=1
    for br in $brlist; do
        br_network=`nmcli dev show $br | grep IP4.ADDRESS | awk '{print $2}'`
        echo " $cnt) $br - $br_network"
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
            bridge=`echo $br`
            break
        fi
        cnt=`expr $cnt + 1`
    done

    if [ X"$bridge" = X ] ; then
        echo "Invalid choice"
        exit
    fi
}

setup_storage() {
    # I'm sure there is a cleaner way to do this, but hey it works
    pool_list=`virsh pool-list --details | sed -n '3,99p' | sed '/^$/d' \
        | awk '{print $1}'`

    echo -e "${green}Select a storage pool:${end}"
    cnt=1
    for pool in $pool_list; do
        pool_path=`virsh pool-dumpxml $pool | grep path | sed 's/^[ ]*//'`
        echo " $cnt) $pool - $pool_path"
        cnt=`expr $cnt + 1`
    done
    echo " q) quit"

    # select storage pool
    poolsel=
    while [ X"$poolsel" = X ] ; do
        echo -n "select : "
        read poolsel
    done

    [ $poolsel = "q" ] && exit
    cnt=1
    for pool in $pool_list; do
        if [ $cnt -eq $poolsel ] ; then
            pool=`echo $pool`
            break
        fi
        cnt=`expr $cnt + 1`
    done

    if [ X"$pool" = X ] ; then
        echo "Invalid choice"
        exit
    fi

}

select_iso() {
    if [ ! -d $iso_loc ] ; then
        echo "$iso_loc does not exist, so no isos available to install from."
        exit
    fi
    echo -e "${green}Select iso for OS installation:${end}"
    isolist=`find $iso_loc -name *.iso -exec basename "{}" \;`
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

    iso=`find $iso_loc -name $isoname`
    [ ! -f ${iso} ] && (echo "${iso} does not exist!" ; exit)
}

select_os() {
    if [ `hostname -s` = $HSRV ] ; then
        osroot=http://$HSRV.dlr.com/pub/distros
    else
        osroot=http://solo.dlr.com/pub/distros
    fi

    # use 'osinfo-query os' to get available osvariant values
    if [ $distro = r90 ] ; then
        osvariant="rhel7.5"
        osdir="${osroot}/rhel/9/"
        ks="inst.geoloc=0 ks=${osroot}/rhel/ks9.cfg"
    elif [ $distro = r86 ] ; then
        osvariant="rhel7.5"
        osdir="${osroot}/rhel/8/"
        ks="inst.geoloc=0 ks=${osroot}/rhel/ks8.cfg"
    elif [ $distro = c84 ] ; then
        osvariant="centos7.0"		# latest for CentOS 8.x
        osdir="${osroot}/centos/8/"
        ks="ks=${osroot}/centos/ks8.cfg"
    elif [ $distro = f36 ] ; then
        osvariant="fedora28"
        osdir="${osroot}/fedora/36"
        ks="ks=${osroot}/fedora/ks-fedora.cfg"
    else
        echo "Invalid parameter. Now what do I do with storage volume?"
        return
    fi
}

# Process args
[ $# -lt 12 ] && usage		# Minimum is 5 params + value = 10
while [[ $# -gt 1 ]]
do
key="$1"
case $key in
    -h|--help)
    usage
    ;;
    -n|--name)
    vm="$2"
    shift
    ;;
    -v|--cpu)
    vcpu="$2"
    shift
    ;;
    -r|--ram)
    ram="$2"
    # Fedora 25 install fails with "no space left on device" error
    [ $ram -le 1 ] && echo -e "${red}WARNING: RAM < 1 GB may cause install \
         problems with some operating systems!${end}"
    ramf=`echo $ram \* 1024 | bc -l`	# convert from GB to MB
    ram=${ramf/.*}			# convert float to int
    shift
    ;;
    -s|--disk)
    disk="$2"
    [ $disk -le 8 ] && echo -e "${red}WARNING: You should consider at least \
       8 GB of disk space!${end}"
    shift
    ;;
    -o|--osvariant)
    osvariant="$2"
    shift
    ;;
    -p|--pool)
    pool="$2"
    shift
    ;;
    -i|--install)
    install="$2"
    [ $2 = "pxe" -o $2 = "iso" -o $2 = "net" ] && shift || usage
    ;;
    -d|--distro)
    distro="$2"
    match=0
    for d in $supported_distros ; do
        [ "$d" = "$distro" ] && match=1	# could be better
    done
    [ $match = 1 ] && shift || usage
    ;;
    -g|--vnc)
    vnc="$2"
    [ $2 = "yes" -o $2 = "no" ] && shift || usage
    ;;
    -b|--bridge)
    bridge="$2"
    shift
    ;;
    -m|--mac)
    mac="$2"
    shift
    ;;
    *)

    ;;
esac
shift
done

# Make sure we have all parameters we need
[ $vnc = "yes" ] && graph="vnc" || graph="none"
[ X"$vm" = X ] && usage
[ X"$install" = X ] && usage
[ X"$osvariant" = X ] && usage

check_requirements
[ X"$bridge" = X ] && setup_bridge			# need to validate
[ X"$pool" = X ] && setup_storage
storpoolargs="vol=${pool}/${vm}"
echo -e "${green}Creating storage volume $vm in pool $pool${end}"
virsh vol-create-as $pool $vm ${disk}G --format qcow2

# Build args to pass depending on what was provided (or not)
[ ! X"$mac" = X ] && params_to_pass="--mac=\"$mac\" "	# need to validate

# Select installation method
if [ "$install" = "iso" ] ; then
    select_iso
    params_to_pass=$params_to_pass" --cdrom=$iso"
elif [ "$install" = "pxe" ] ; then
    params_to_pass=$params_to_pass" --pxe"
elif [ "$install" = "net" ] ; then
    tty="console=tty0 console=ttyS0,115200"
    select_os
    params_to_pass=$params_to_pass" --location=$osdir"
    extra_args="$ks $tty"
else
    usage
fi

if [ $install = "iso" -o $install = "pxe" ] ; then
    virt-install --connect qemu:///system \
       --network bridge=${bridge},model="virtio" \
       --name $vm --ram=$ram --vcpus=$vcpu --disk ${storpoolargs} \
       --os-variant=${osvariant} \
       --graphics ${graph} $params_to_pass
else
    virt-install --connect qemu:///system \
       --network bridge=${bridge},model="virtio" \
       --name $vm --ram=$ram --vcpus=$vcpu --disk ${storpoolargs} \
       --os-variant=${osvariant} \
       --graphics ${graph} $params_to_pass --extra-args="$extra_args"
fi

# 2022.12.07 08:32:13 - JD
