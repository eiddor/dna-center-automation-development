# Cisco ~~DNA~~ Catalyst Center Basic Automation
I've created this repo to help me setup a basic config on Cisco Catalyst Center for my lab environment.

It's similar to this: https://github.com/eiddor/ise-automation-python

Original repo is here: https://github.com/cisco-en-programmability/dnacenter_fabric_operations

This repo uses Cisco Catalyst Center REST APIs to:

- create a new area, buildings, and floors
- populate network settings
- create new Global pool, Reserve subpools and LAN pools for LAN Automation and SDA Transit


**Cisco Products & Services:**

- Cisco Catalyst Center

**Tools & Frameworks:**

- Python virtual environment to run the application
- Cisco DNA Center Python SDK

**Usage**

- Create a new Python virtual environment, and activate it - https://docs.python.org/3.9/library/venv.html


- Install the Python libraries from the "requirements.txt" file -
    - (venv) dnacenter_fabric_operations % pip3 install -r requirements.txt


- Create your "environment.env" file:

```
# Cisco DNA Center
DNAC_URL = 'DNA Center URL/IP address'
DNAC_USER = 'username'
DNAC_PASS = 'password'
```

- Sample "fabric_operations.yml"

```
area_info:
  name: OR
  hierarchy: Global

building_info:
  name: BEAV
  address: 1600 Northeast Compton Drive, Beaverton, Oregon 97006, United States
  lat: 45.532297
  long: -122.881111

floor_info:
  name: Main
  number: 1
  rf_model: Cubes And Walled Offices
  width: 100
  length: 50
  height: 10

network_settings:
  dns_server: 171.70.168.183
  dhcp_server: 10.93.141.1
  ntp_server: 171.68.38.66
  syslog_server: 10.93.141.37
  aaa_server: 10.93.141.38

devices_info:
  device_ips: [10.93.141.20, 10.93.141.28, 10.93.141.17]
  device_roles: [control-plane, border, edge]

fabric_info:
  name: Main

ip_pool:
  name: Global_Fabric_Pool
  type: Generic
  subnet: 10.200.0.0/20
  gateway: 10.200.1.1
  dhcp_server: 10.93.141.46
  dns_server: 10.93.141.46
  address_family: IPv4

ip_sub_pool:
  name: BEAV_Fabric_Subpool
  type: Generic
  subnet: 10.200.1.0/24
  gateway: 10.200.1.1
  dhcp_server: 10.93.141.46
  dns_server: 10.93.141.46
  address_family: IPv4

ip_transit_pool:
  name: BEAV_Transit_Pool
  type: Generic
  subnet: 10.200.2.0/24
  gateway: 10.200.2.1
  dhcp_server: 10.93.141.46
  address_family: IPv4

l3_vn:
  name: Servers

control_plane_devices:
  ip: [10.93.141.20]

border_devices:
  ip: [10.93.141.28]
  routing_protocol: BGP
  internal_bgp_as: 65001
  external_bgp_as: 65002
  external_interface: TenGigabitEthernet1/1/1
  transit_network: IP_Transit
  transit_vlan: 602

edge_devices:
  ip: [10.93.141.17]

auth_profile:
  name: No Authentication

```

- Create using the Cisco DNA Center UI an IP transit network (if not already existing). 
In the provided "fabric_operations.yml" file the name of the IP transit network is "IP_Transit" 


- The command to run the SDA-as-Code app:

    - (venv) dnacenter_fabric_operations % python3 create_fabric_site.py


-------


**License**

This project is licensed to you under the terms of the [Cisco Sample Code License](./LICENSE).


