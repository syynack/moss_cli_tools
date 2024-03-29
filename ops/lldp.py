#!/usr/bin/python

import sys
import json
import re

from ops import log
from ops.connection import Session


def _get_lldp_neighbors_json(switch):
    session = Session().ssh(switch)
    
    command = 'lldpctl -f xml'
    output = session.send_command(command)
    
    output_dict = {}
    regexes = ['id\slabel.*"mac">(?P<remote_chassis_ll_addr>[^<]+)',
               'name\slabel.*"SysName">(?P<remote_hostname>[^<]+)',
               'id\slabel="PortID".*"mac">(?P<remote_port_ll_addr>[^<]+)',
               'descr\slabel="PortDescr">(?P<remote_port_id>[^<]+)'
              ]
    
    for line in output.splitlines():
        if 'interface label' in line:
            port_id = str(line.split()[2].split('=')[1].replace('"', ''))
            output_dict[port_id] = {}
            
        for regex in regexes:
            match = re.search(regex, line)
            
            if match:
                output_dict[port_id].update(match.groupdict())
              
    return output_dict
       

def _print_lldp_neighbors(output):
    table_format = '{:<10} {:<16} {:<20} {:<16} {}'
    
    print ''
    print table_format.format('Port ID', 'Remote Hostname', 'Remote Chassis MAC', 'Remote Port ID', 'Remote Port MAC')
    
    for neighbor in output:
        print table_format.format(neighbor, output[neighbor]['remote_hostname'], output[neighbor]['remote_chassis_ll_addr'],
            output[neighbor]['remote_port_id'], output[neighbor]['remote_port_ll_addr']
        )
        
    print ''


def get_lldp_neighbors_for_specific_interface_in_json(switch, int):
    output = _get_lldp_neighbors_json(switch)
    input = {}
    
    for interface in output:
        if interface == int:
            input[interface] = output[interface]
            
    print json.dumps(input, sort_keys=True, indent=4, separators=(',', ': '))


def get_lldp_neighbors_in_json(switch):
    output = _get_lldp_neighbors_json(switch)
    print json.dumps(output, sort_keys=True, indent=4, separators=(',', ': '))


def get_lldp_neighbors_for_specific_interface(switch, int):
    output = _get_lldp_neighbors_json(switch)
    input = {}
    
    for interface in output:
        if interface == int:
            input[interface] = output[interface]
            
    _print_lldp_neighbors(input)
            

def get_lldp_nighbors(switch):
    output = _get_lldp_neighbors_json(switch)
    _print_lldp_neighbors(output)