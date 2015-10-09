#!/bin/bash
# Stop all containers

# Exit if binary not found, because error is ugly
x=`which docker 1> /dev/null 2>&1`
if [ $? -eq 1 ] ; then
  echo "docker not installed"
  exit 1
fi

# Get a list of *all* containers (running or not)
conts=`docker ps -a | tail -n +2 | awk '{print $1}'`

for c in $conts; do
   pid=`docker inspect -f '{{.State.Pid}}' $c`
   docker stop ${c}
done

# 2015.06.17 17:24:02 - JD
