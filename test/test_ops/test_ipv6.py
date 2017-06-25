#!/usr/bin/python

import json
import re

from test_ops import test_log

def _get_ipv6_json(switch):
    ifconfig_output = '''
eth0      Link encap:Ethernet  HWaddr 02:42:ac:11:00:02
          inet6 addr: fe80::42:acff:fe11:2/64 Scope:Link
          inet6 addr: fd35:1:1:1::1/128 Scope:Global
lo        Link encap:Local Loopback
          inet6 addr: ::1/128 Scope:Host
    '''
    previous_port = ''
    inet6_addrs = {}
    
    for line in ifconfig_output.splitlines():
        if 'Link encap' in line:
            port_id = line.split()[0]
            previous_port = port_id
            
            if port_id not in inet6_addrs:
                inet6_addrs[port_id] = []
                
        elif 'inet6' in line:
            addr = line.split()[2]
            inet6_addrs[previous_port].append(addr)
            
                
    return inet6_addrs
            

def _print_ipv6_table(ipv6_json):
    table_format = '{:<15} {}'
    
    print ''
    print table_format.format('Port ID', 'Addresses')

    for interface in ipv6_json:
        print table_format.format(interface, ipv6_json[interface][0])
        
        for address in ipv6_json[interface][1:]:
            print table_format.format('', address)
            
    print ''


def get_ipv6_addresses(switch):
    ipv6_json = _get_ipv6_json(switch)

    _print_ipv6_table(ipv6_json)
        

def get_ipv6_addresses_in_json(switch):
    ipv6_json = _get_ipv6_json(switch)

    print json.dumps(ipv6_json, sort_keys=True, indent=4, separators=(',', ': '))
