#!/usr/bin/python

import sys
import json
import re

from ops.connection import Session


def _get_nd_table_json(switch):
    session = Session().ssh(switch)
    
    output = session.send_command('ip -6 neighbor show')

    regex = '(?P<inet6_addr>[^\s]+)\sdev\s(?P<port_id>[^\s]+)\slladdr\s(?P<ll_addr>[^\s]+)\srouter\s(?P<state>[^\n]+)'
    output_dict = []

    for line in output.splitlines():
        data = re.search(regex, line)
        if data is not None:
            data = data.groupdict()
            output_dict.append(data)
            
    return output_dict


def _print_nd_table(nd_table):
    table_format = '{:<30} {:<20} {:<10} {}'
    print ''
    print table_format.format('IPv6 Address', 'MAC address', 'Port ID', 'State')
    
    for neighbor in nd_table:
        print table_format.format(
            neighbor["inet6_addr"], neighbor["ll_addr"], neighbor["port_id"], neighbor["state"]
        )

    print ''

    
def get_neighbor_discovery_table_stale_entries_in_json(switch):
    output = _get_nd_table_json(switch)
    input = {}
    
    for entry in output:
        if entry['state'] == 'STALE':
            input.update(entry)
            
    print json.dumps(input, sort_keys=True, indent=4, separators=(',', ': '))


def get_neighbor_discovery_table_reachable_entries_in_json(switch):
    output = _get_nd_table_json(switch)
    input = {}
    
    for entry in output:
        if entry['state'] == 'REACHABLE':
            input.update(entry)
            
    print json.dumps(input, sort_keys=True, indent=4, separators=(',', ': '))


def get_neighbor_discovery_table_entries_in_json(switch):
    output = _get_nd_table_json(switch)
    print json.dumps(output, sort_keys=True, indent=4, separators=(',', ': '))


def get_neighbor_discovery_table_stale_entries(switch):
    output = _get_nd_table_json(switch)
    input = []
    
    for entry in output:
        if entry['state'] == 'STALE':
            input.append(entry)
            
    _print_nd_table(input)


def get_neighbor_discovery_table_reachable_entries(switch):
    output = _get_nd_table_json(switch)
    input = []
    
    for entry in output:
        if entry['state'] == 'REACHABLE':
            input.append(entry)
            
    _print_nd_table(input)


def get_neighbor_discovery_table_entries(switch):
    output = _get_nd_table_json(switch)
    _print_nd_table(output)