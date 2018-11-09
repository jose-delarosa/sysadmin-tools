#!/usr/bin/env python
# Copyright 2018 Jose Delarosa
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
