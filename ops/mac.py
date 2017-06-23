#!/usr/bin/python

import json
import re

from ops.connection import Session
from ops import log

#

def _get_macs_json(switch):
    session = Session().ssh(switch)
    
    command = 'ifconfig'
    output = session.send_command(command)
    
    output_dict = []
    regex = r'(?P<port_id>([^\s]+)).*?\sHWaddr\s(?P<ll_addr>([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2}))'
    
    for line in output.splitlines():
        data = re.search(regex, line)
        if data is not None:
            output_dict.append(data.groupdict())
    
    return output_dict


def _print_macs_table(macs_json):
    table_format = '{:<15} {}'

    print ''
    print table_format.format('Port ID', 'MAC address')
        
    for mac in macs_json:
        print table_format.format(mac["port_id"], mac["ll_addr"])
            
    print ''


def get_interface_mac_addresses(switch):
    macs_json = _get_macs_json(switch)
        
    _print_macs_table(macs_json)
        
        
def get_interface_mac_addresses_in_json(switch):
    macs_json = _get_macs_json(switch)

    print json.dumps(macs_json, sort_keys=True, indent=4, separators=(',', ': '))