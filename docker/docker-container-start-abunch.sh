#!/bin/bash
# Script to start a bunch of containers for demonstration purposes ONLY.
# TODO: check that $2 is an int

# Exit if binary not found, because error is ugly
x=`which docker 1> /dev/null 2>&1`
if [ $? -eq 1 ] ; then
   echo "docker not installed"
   exit 1
fi

if [ $# -lt 2 ] ; then
   echo "usage: `basename $0` <image> <instances>"
   exit 1
fi

im=$1
no=$2

# check that image exists
all=`docker images | tail -n +2 | awk '{print $1":"$2}'`
for a in $all; do
   if [ "$im" = "$a" ] ; then
      co=`echo $im | cut -d":" -f1`
      for (( i=1; i<=$no; i++)); do
         docker run -d -P --name=${co}-${i} ${im}
      done
      exit 0
   fi
done

echo "Image $im not valid!"
