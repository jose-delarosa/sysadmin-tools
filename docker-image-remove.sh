#!/bin/bash
# Remove Docker images. Will not remove if an image is being used.

oflag=0				# override flag

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
      [ $1 = "-y" ] && oflag=1
   fi
}

ask() {
   if [ $oflag -eq 0 ] ; then
      echo -n "Are you sure you want to continue? [y/N] : "
      read resp
      case $resp in
         y ) echo "Ok" ; return ;;
         * ) echo "Aborting." ; exit 1 ;;
      esac
   fi
}

remove() {
   # Get a list of all images
   imgs=`docker images | tail -n +2 | awk '{print $1}'`

   for i in $imgs; do
      # docker rmi $i
      echo "docker rmi $i"
   done
}

chkreqs
parse
ask
remove

