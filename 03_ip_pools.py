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
    print('\nConfigure Network Settings script start, ', current_time)

    with open('site_info.yaml', 'r') as file:
        project_data = yaml.safe_load(file)

    print('\n\nProject Details:\n')
    pprint(project_data)

    # Create a DNACenterAPI "Connection Object"
    dnac_api = DNACenterAPI(username=DNAC_USER, password=DNAC_PASS, base_url=DNAC_URL, version='2.2.3.3', verify=False)

    # get Cisco DNA Center Auth token
    dnac_auth = get_dnac_token(DNAC_AUTH)


    ip_pool_name = project_data['ip_pool']['name']
    ip_pool_type = project_data['ip_pool']['type']
    ip_pool_cidr = project_data['ip_pool']['subnet']
    ip_pool_address_space = project_data['ip_pool']['address_family']

    # ip_transit_pool_name = project_data['ip_transit_pool']['name']
    # ip_transit_pool_type = project_data['ip_transit_pool']['type']
    # ip_transit_pool_cidr = project_data['ip_transit_pool']['subnet']
    # ip_transit_pool_gateway = project_data['ip_transit_pool']['gateway']
    # ip_transit_pool_dhcp_server = project_data['ip_transit_pool']['dhcp_server']
    # ip_transit_pool_address_space = project_data['ip_transit_pool']['address_family']

    # create a new Global Pool
    print('\n\nCreating the Global Pool: ', ip_pool_name)
    global_pool_payload = {
        'settings': {
            'ippool': [
                {
                    'ipPoolName': ip_pool_name,
                    'type': ip_pool_type,
                    'ipPoolCidr': ip_pool_cidr,
                    'IpAddressSpace': ip_pool_address_space
                }
            ]
        }
    }
    response = dnac_api.network_settings.create_global_pool(payload=global_pool_payload)
    time_sleep(10)


    for pool in project_data['ip_sub_pool']:
        ip_sub_pool_name = pool['name']
        ip_sub_pool_type = pool['type']
        ip_sub_pool_cidr = pool['subnet']
        ip_sub_pool_gateway = pool['gateway']
        ip_sub_pool_dhcp_server1 = pool['dhcp_server1']
        ip_sub_pool_dhcp_server2 = pool['dhcp_server2']
        ip_sub_pool_dns_server1 = pool['dns_server1']
        ip_sub_pool_dns_server2 = pool['dns_server2']
        ip_sub_pool_address_space = pool['address_family']
    
        # create an IP sub_pool for site_hierarchy
        ip_sub_pool_subnet = ip_sub_pool_cidr.split('/')[0]
        ip_sub_pool_mask = int(ip_sub_pool_cidr.split('/')[1])
        print('\n\nCreating the IP subpool: ', ip_sub_pool_cidr)
        sub_pool_payload = {
            'name': ip_sub_pool_name,
            'type': ip_sub_pool_type,
            'ipv4GlobalPool': ip_pool_cidr,
            'ipv4Prefix': True,
            'ipv6AddressSpace': False,
            'ipv4PrefixLength': ip_sub_pool_mask,
            'ipv4Subnet': ip_sub_pool_subnet,
            'ipv4GateWay': ip_sub_pool_gateway,
            'ipv4DhcpServers': [
                ip_sub_pool_dhcp_server1, ip_sub_pool_dhcp_server2
                ],
            'ipv4DnsServers': [
                ip_sub_pool_dns_server1, ip_sub_pool_dns_server2
                ]
            }
        # get the site_id
        area_name = pool['area']
        building_name = pool['building']
        site_hierarchy = 'Global/' + area_name + '/' + building_name
        response = dnac_api.sites.get_site(name=site_hierarchy)
        site_id = response['response'][0]['id']
        response = dnac_api.network_settings.reserve_ip_subpool(site_id=site_id, payload=sub_pool_payload)
        time_sleep(10)

    # # create an IP transit pool for site_hierarchy
    # print('\n\nCreating the IP transit pool: ', ip_transit_pool_cidr)
    # ip_transit_pool_subnet = ip_transit_pool_cidr.split('/')[0]
    # ip_transit_pool_mask = int(ip_transit_pool_cidr.split('/')[1])
    # transit_pool_payload = {
    #     'name': ip_transit_pool_name,
    #     'type': ip_transit_pool_type,
    #     'ipv4GlobalPool': ip_pool_cidr,
    #     'ipv4Prefix': True,
    #     'ipv6AddressSpace': False,
    #     'ipv4PrefixLength': ip_transit_pool_mask,
    #     'ipv4Subnet': ip_transit_pool_subnet,
    #     'ipv4GateWay': ip_transit_pool_gateway,
    #     'ipv4DhcpServers': [
    #         ip_transit_pool_dhcp_server
    #         ],
    #     'ipv6Prefix': True,
    #     'ipv6GlobalPool': '2001:2021::1000/64',
    #     'ipv6PrefixLength': 96,
    #     'ipv6Subnet': '2001:2021::1000'
    #     }
    # response = dnac_api.network_settings.reserve_ip_subpool(site_id=site_id, payload=transit_pool_payload)
    # time_sleep(10)





    # get the site_id
    print('\n\nConfiguring Network Settings:')
    pprint(project_data['network_settings'])
    response = dnac_api.sites.get_site(name=site_hierarchy)
    site_id = response['response'][0]['id']
    response = dnac_api.network_settings.create_network(site_id=site_id, payload=network_settings_payload)
    time_sleep(10)

if __name__ == '__main__':
    sys.exit(main())