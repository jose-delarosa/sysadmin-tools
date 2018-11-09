#!/usr/bin/python
#
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
#
# Script to check the power state (On/Off) of a remote server through
# an Out-Of-Band controller using Redfish APIs.

import json
import sys
import requests
from urllib2 import URLError, HTTPError
# http://bit.ly/2iGTEGS
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Is this the standard?
redfish_uri = "/redfish/v1"


def usage(me):
    print("Usage: %s <ip> <user> <password>" % (me))
    exit(1)


def send_get_request(uri, creds):
    try:
        resp = requests.get(uri, verify=False,
                            auth=(creds['user'], creds['pswd']))
        data = resp.json()
    except HTTPError as e:
        return {'ret': False, 'msg': "HTTP Error: %s" % e.code}
    except URLError as e:
        return {'ret': False, 'msg': "URL Error: %s" % e.reason}
    # Almost all errors should be caught above, but just in case
    except:
        return {'ret': False, 'msg': "Error"}
    return {'ret': True, 'data': data}


def find_systems_resource(base_uri, creds):
    systems_uri = []
    response = send_get_request(base_uri + redfish_uri, creds)

    if response['ret'] is False:
        return {'ret': False, 'msg': "Error getting Systems resource"}
    data = response['data']

    if 'Systems' not in data:
        return {'ret': False, 'msg': "Systems resource not found"}
    else:
        systems = data["Systems"]["@odata.id"]
        response = send_get_request(base_uri + systems, creds)
        if response['ret'] is False:
            return {'ret': False, 'msg': "Couldn't get Systems resource value"}
        data = response['data']

        # more than one entry possible, so put in a list
        for member in data[u'Members']:
            systems_uri.append(member[u'@odata.id'])
        return {'ret': True, 'systems_uri': systems_uri}


def check_power_state(base_uri, uris_list, creds):
    for uri in uris_list:
        response = send_get_request(base_uri + uri, creds)
        if response['ret'] is False:
            print("Couldn't get power information")
            return
        data = response['data']
        print("Server Power: %s" % data[u'PowerState'])
    return

def main():
    if len(sys.argv) < 4:
        usage(sys.argv[0])

    # Disable insecure-certificate-warning message
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    base_uri = "https://" + sys.argv[1]
    creds = {'user': sys.argv[2],
             'pswd': sys.argv[3]}

    # This will vary by OEM
    result = find_systems_resource(base_uri, creds)

    if result['ret'] is True:
        check_power_state(base_uri, result['systems_uri'], creds)
    else:
        print("Error: %s" % result['msg'])
        exit(1)


if __name__ == '__main__':
    main()
