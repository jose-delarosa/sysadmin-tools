#!/usr/bin/env python
#
# Copyright (c) 2013, Dell Inc.
# All rights reserved.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms and conditions of the GNU General Public License version 2,
# as published by the Free Software Foundation.
#
# Author: Jose De la Rosa <jose_de_la_rosa@dell.com>

# Generate random alphanumeric strings that could be used for passwords. These
# two functions do the exact same thing, it's just a different way of doing it
# to show python's versatility.

import string
from random import choice

def GenPasswd1(len):
   passwd = ''
   chars = string.letters + string.digits
   for i in range(len):
      passwd = passwd + choice(chars)
   return passwd

def GenPasswd2(length, chars):
   return ''.join([choice(chars) for i in range(length)])

pass1 = GenPasswd1(8)
pass2 = GenPasswd2(12, string.letters + string.digits)

print "Random strings for passwords\n"
print " 8 chars long: %s" % pass1
print "12 chars long: %s" % pass2
