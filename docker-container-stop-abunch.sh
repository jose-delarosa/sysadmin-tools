#!/bin/bash
#
# Script to start a bunch of containers for demonstration purposes ONLY.
# TODo: check that $2 is an int

# Exit if binary not found, because error is ugly
x=`which docker 1> /dev/null 2>&1`
if [ $? -eq 1 ] ; then
  echo "docker not installed"
  exit 1
fi

if [ $# -lt 2 ] ; then
   echo "usage: `basename $0` <container> <instances>"
   exit 1
fi

cont=$1
no=$2

for (( i=1; i<=$no; i++)); do
   docker stop ${cont}-${i} 1> /dev/null 2>&1
   docker rm ${cont}-${i}
done

# 2015.02.13 12:22:45 - JD
