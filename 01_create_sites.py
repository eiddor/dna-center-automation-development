#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (c) 2021 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
               https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

__author__ = "Gabriel Zapodeanu TME, ENB"
__email__ = "gzapodea@cisco.com"
__version__ = "0.1.0"
__copyright__ = "Copyright (c) 2021 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"


import os
import time
import requests
import urllib3
import json
import sys
import logging
import datetime
import yaml

from urllib3.exceptions import InsecureRequestWarning  # for insecure https warnings
from dotenv import load_dotenv
from dnacentersdk import DNACenterAPI
from datetime import datetime
from pprint import pprint
from requests.auth import HTTPBasicAuth  # for Basic Auth

urllib3.disable_warnings(InsecureRequestWarning)  # disable insecure https warnings

load_dotenv('environment.env')

DNAC_URL = os.getenv('DNAC_URL')
DNAC_USER = os.getenv('DNAC_USER')
DNAC_PASS = os.getenv('DNAC_PASS')

os.environ['TZ'] = 'America/Los_Angeles'  # define the timezone for PST
time.tzset()  # adjust the timezone, more info https://help.pythonanywhere.com/pages/SettingTheTimezone/

DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)


def time_sleep(time_sec):
    """
    This function will wait for the specified time_sec, while printing a progress bar, one '!' / second
    Sample Output :
    Wait for 10 seconds
    !!!!!!!!!!
    :param time_sec: time, in seconds
    :return: none
    """
    print('\nWait for ' + str(time_sec) + ' seconds')
    for i in range(time_sec):
        print('!', end='')
        time.sleep(1)
    return

def get_dnac_token(dnac_auth):
    """
    Create the authorization token required to access Cisco DNA Center
    Call to Cisco DNA Center - /api/system/v1/auth/login
    :param dnac_auth - Cisco DNA Center Basic Auth string
    :return Cisco DNA Center Token
    """
    url = DNAC_URL + '/dna/system/api/v1/auth/token'
    header = {'content-type': 'application/json'}
    response = requests.post(url, auth=dnac_auth, headers=header, verify=False)
    response_json = response.json()
    dnac_jwt_token = response_json['Token']
    return dnac_jwt_token

def create_fabric_site(site_hierarchy, dnac_token):
    """
    This function will create a new fabric at the site with the hierarchy {site_hierarchy}
    :param site_hierarchy: site hierarchy, for example {Global/OR/PDX-1/Floor-2}
    :param dnac_token: Cisco DNA Center auth token
    :return: response in JSON
    """
    payload = {
        "siteNameHierarchy": site_hierarchy
    }
    url = DNAC_URL + '/dna/intent/api/v1/business/sda/fabric-site'
    header = {'content-type': 'application/json', 'x-auth-token': dnac_token}
    response = requests.post(url, data=json.dumps(payload), headers=header, verify=False)
    response_json = response.json()
    return response_json

def main():
    """
    This script will create a new fabric at the site specified in the param provided.
    """

    # logging, debug level, to file {application_run.log}
    logging.basicConfig(
        filename='application_run.log',
        level=logging.DEBUG,
        format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')

    current_time = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print('\nCreate Fabric App Start, ', current_time)

    with open('site_info.yaml', 'r') as file:
        project_data = yaml.safe_load(file)

    print('\n\nProject Details:\n')
    pprint(project_data)

    # Create a DNACenterAPI "Connection Object"
    dnac_api = DNACenterAPI(username=DNAC_USER, password=DNAC_PASS, base_url=DNAC_URL, version='2.2.3.3', verify=False)

    # get Cisco DNA Center Auth token
    dnac_auth = get_dnac_token(DNAC_AUTH)

# iterate through the list of areas and create them using the information in site_info.yaml
    for name in project_data['area_info']:
                # create a new area
                print('\nCreating a new area:', name['name'])
                area_payload = {
                    "type": "area",
                    "site": {
                        "area": {
                            "name": name['name'],
                            "parentName": name['hierarchy']
                        }
                    }
                }
                response = dnac_api.sites.create_site(payload=area_payload)
                time_sleep(10)


# iterate through the list of buildings and create them using the information in site_info.yaml
    for name in project_data['building_info']:
                # create a new building
                print('\n\nCreating a new building:', name['name'])
                building_payload = {
                    'type': 'building',
                    'site': {
                        'building': {
                            'name': name['name'],
                            'parentName': 'Global/' + name['area'],
                            'address': name['address'],
                            'latitude': name['lat'],
                            'longitude': name['long']
                        }
                    }
                }
                response = dnac_api.sites.create_site(payload=building_payload)
                print(response.text)
                time_sleep(10)


if __name__ == '__main__':
    sys.exit(main())