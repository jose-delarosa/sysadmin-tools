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

# Print array of ANSI colors.
# Foreground color codes:
# 30=black 31=red 32=green 33=yellow 34=blue 35=magenta 36=cyan 37=white
# Background color codes:
# 40=black 41=red 42=green 43=yellow 44=blue 45=magenta 46=cyan 47=white

import sys, subprocess

attr = [0,1,4,5,6,7]
for index in range(len(attr)):
  print "\n"   # helps keep things somewhat clean. This color-printing business can get pretty messy.
  print "ESC[%s;Foreground;Background" % (attr[index])
  # in range(), second number is not part of the list, so here it's 30 - 37
  for fore in range(30, 38):
    for back in range(40, 48):
      subprocess.call('printf \'\033[%s;%s;%sm %02s;%02s \'' % (attr[index],fore,back,fore,back), shell=True)
    subprocess.call('printf \'\n\'', shell=True)
  subprocess.call('printf \'\033[0m\'', shell=True)
