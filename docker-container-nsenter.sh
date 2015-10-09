#!/bin/bash
# Very dum script to enter into it

bins="docker nsenter"
for bin in $bins; do
   x=`which $bin 1> /dev/null 2>&1`
   if [ $? -eq 1 ] ; then
      echo "$bin not installed"
      exit 1
   fi
done

if [ $# -lt 1 ] ; then
   echo "usage: `basename $0` <container>"
   exit 1
fi

pid=`docker inspect -f "{{ .State.Pid }}" $1`
if [ "$pid" = "<no value>" ] ; then
   echo "No container found."
   exit 1
fi
nsenter -m -u -n -i -p -t $pid /bin/bash

# 2015.01.21 16:42:01 - JD
