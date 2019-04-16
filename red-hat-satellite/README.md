# What does code do

A collection of scripts to demonstrate usage of the Satellite 6 API

* purge-satellite-hosts.py: Removes registered clients that have not checked-in in a given number of days.

# What versions does it work on

This script has been tested and works on:

* Satellite v6.4

# Prerequisites

* Python >= 2.7
* Python >= 3.6
* Python `requests` module
* A login ID to Satellite with admin privileges

# How to run your code

~~~
$ purge-satellite-hosts --help
usage: purge-satellite-hosts [-h] -u USER -p PASSWORD -s SAT -d DAYS

Purge client hosts that have not checked-in in n days

optional arguments:
  -h, --help            show this help message and exit
  -u USER, --user USER  User for authentication
  -p PASSWORD, --password PASSWORD
                        Password for authentication
  -s SAT, --satellite SAT
                        Red Hat Satellite server
  -d DAYS, --days DAYS  Days clients have not checked-in for

$ purge-satellite-hosts.py -u admin -p password -s satellite.example.com -d 10
~~~

# Example Output

Since this script is meant to be run as a cron job, all output is directed to a log file specified by the variables `LOG_DIR` and `LOG_FILE`.

Example log file:
~~~
$ cat purge-hosts.log.20190410-050101
Current Time: 2019-04-10 05:01:02.578768

Servers Check-in Time:
ans1.br0.com, 2019-04-10 09:46:27, OK
host-57.br0.com, 2019-04-08 14:50:34, Threshold exceeded!
host-98.br0.com, 2019-04-08 15:48:41, Threshold exceeded!
podman.br0.com, 2019-04-10 07:11:38, OK
r74ehac61.gse.sap.com, 2019-04-09 23:12:41, OK
red1.oselinux.com, 2019-04-08 21:06:49, Threshold exceeded!
red3.oselinux.com, 2019-04-10 09:30:57, OK
red4.oselinux.com, 2019-04-10 07:22:06, OK
stor1.hpc.cluster, 2019-04-10 09:33:04, OK
stor2.hpc.cluster, 2019-04-10 08:35:17, OK
storm1.oselinux.com, 2019-04-10 09:27:21, OK
storm2.oseadc.local, 2019-04-10 06:20:17, OK
t630.oselinux.com, 2019-04-10 09:27:50, OK

Hosts purged: 3
~~~

# Known issues

* None that we are aware of

# Support

This script is provided as-is and it is not supported by Red Hat or Dell EMC.
