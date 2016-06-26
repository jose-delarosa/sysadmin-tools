#!/bin/bash
# Remove Docker containers. Only removes containers that are not running.
# Pass '-f' option to force removal of all containers, including those running.

fflag=0					# 'force' flag

usage() {
   echo "Usage: `basename $0` [-f|-h]"
   echo " -f	also remove running containers"
   echo " -h	print this"
   exit 0
}

chkreqs() {
   # Exit if binary not found, because error is ugly
   x=`which docker 1> /dev/null 2>&1`
   if [ $? -eq 1 ] ; then
      echo "docker not installed"
      exit 1
   fi
}

parse() {
   if [ $# -eq 1 ] ; then
      [ $1 = "-h" ] && usage
      [ $1 = "-f" ] && fflag=1
   fi
}

remove() {
   # Get a list of *all* containers (running or not)
   conts=`docker ps -a | tail -n +2 | awk '{print $1}'`

   for c in $conts; do
      # If 'force' flag is set, then stop it so it can be removed
      [ $fflag = 1 ] && docker stop ${c} 1> /dev/null 2>&1

      pid=`docker inspect -f '{{.State.Pid}}' $c`
      # Only interested if pid = 0 (not running)
      if [ $pid -eq 0 ] ; then
         name=`docker inspect -f '{{.Name}}' $c | cut -d"/" -f2`
         # Remove only if not "regdata" (data volume container for registry)
         if [ ! "$name" = "regdata" ] ; then
            docker rm ${c}
         fi
      fi
   done
}

chkreqs
parse $1
remove
