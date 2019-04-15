#!/usr/bin/env python

# Copyright (c) 2019, Dell EMC Inc.
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
#
# Script to remove registered hosts to a Red Hat Satellite server that have
# not checked-in in a given number of days.

# Import required modules
try:
    import os
    import requests
    import argparse
    import datetime as dt
    from time import strftime
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
except Exception as e:
    print("Error: %s" % e)
    exit(1)

# Customizable variables
LOG_DIR = "/root/logs/rhs/"
LOG_FILE = "purge-hosts.log"

# Don't change these variables
hosts_purged = 0
space = " "
dot = "."


def get_hosts(user, password, satellite):
    uri = "https://%s/api/hosts" % satellite
    response = requests.get(uri, verify=False, auth=(user, password))
    if not response.status_code == 200:
        print("Something went wrong looking up hosts, exiting")
        exit(1)
    return response.json()


def remove_host(user, password, satellite, host):
    global hosts_purged
    headers = {'content-type': 'application/json'}
    uri = "https://%s/api/v2/hosts/%s" % (satellite, host)
    response = requests.delete(uri, headers=headers, verify=False,
                               auth=(user, password))
    if not response.status_code == 200:
        print("Something went wrong removing host %s", host)
        return
    hosts_purged += 1
    return


def compare_ts(days_limit, last_checkin, daten, timen, fd):
    secs_limit = days_limit * 86400
    last_checkin_date = last_checkin.split(' ')[0].split("-")
    last_checkin_time = last_checkin.split(' ')[-1].split(":")

    # Get the difference in seconds between both sets of files
    # Ex: dt.datetime(2019, 3, 7, 16, 17, 52)
    then = dt.datetime(int(last_checkin_date[0]), int(last_checkin_date[1]),
                       int(last_checkin_date[2]), int(last_checkin_time[0]),
                       int(last_checkin_time[1]), int(last_checkin_time[2]))
    now = dt.datetime(int(daten[0]), int(daten[1]),
                      int(daten[2]), int(timen[0]),
                      int(timen[1]), int(timen[2].split('.')[0]))
    fd.write(" %s," % then)
    if (now - then).total_seconds() > float(secs_limit):
        return 1
    return 0


def my_main():
    # options parsing
    desc = "Purge client hosts that have not checked-in in n days"
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-u', '--user', action='store', dest='user',
                        required='true', help='User for authentication')
    parser.add_argument('-p', '--password', action='store', dest='password',
                        required='true', help='Password for authentication')
    parser.add_argument('-s', '--satellite', action='store', dest='sat',
                        required='true', help='Red Hat Satellite server')
    parser.add_argument('-d', '--days', action='store', dest='days',
                        required='true',
                        help='Days clients have not checked-in for')
    args = parser.parse_args()

    tstamp = strftime("%Y%m%d-%H%M%S")                 # get timestamp

    # Disable insecure-certificate-warning message
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    # create log directory if it doesn't exist
    if not os.path.isdir(LOG_DIR):
        os.makedirs(LOG_DIR)
    fd = open(LOG_DIR + LOG_FILE + dot + tstamp, 'w')  # open file for writing

    # Process current time
    now = str(dt.datetime.now())
    date = now.split()[0].split("-")
    time = now.split()[-1].split(":")
    fd.write("Current Time: %s\n\n" % now)

    fd.write("Client hosts check-in time:\n")
    data = get_hosts(args.user, args.password, args.sat)
    for x in data[u'results']:
        if not x[u'certname'] == args.sat:
            hostname = x[u'certname']
            fd.write("%s," % hostname)

            # Get last checkin for each server and put in right format
            if 'subscription_facet_attributes' in x:
                checkin = x[u'subscription_facet_attributes'][u'last_checkin']
                last_checkin = checkin.split()[0] + space + checkin.split()[1]

                '''
                check if time threshold has been exceeded given days specified
                ret_value = 0 - threshold not exceeded
                ret_value = 1 - threshold exceeded
                '''
                ret_value = compare_ts(args.days, last_checkin, date, time, fd)
                if ret_value == 1:
                    fd.write(" Threshold exceeded!\n")
                    remove_host(args.user, args.password, args.sat, args.hostname)
                else:
                    fd.write(" OK\n")
            else:
                '''
                This can happen, need to know why, and definitely need to
                handle it. At least log it.
                '''
                fd.write(" Last-check-in entry not found! No action taken.\n")

    fd.write("\nHosts purged: %s\n" % hosts_purged)
    fd.close()
    exit(0)


if __name__ == '__main__':
    my_main()
