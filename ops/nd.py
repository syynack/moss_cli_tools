#!/usr/bin/python

import sys
import json
import re



''' Look into regex usage

    import re
    
'''

from ops.connection import Session


def _get_nd_table_json(switch, stale, reachable):
    session = Session().ssh(switch)
    
    nd_table = session.send_command('ip -6 neighbor show')

    regexes = ['(?P<link_local>(fe80:(:[0-9a-fA-F]{0,4}){0,4}))',
               '(?P<port_id>(dev (\w+)))',
               '(?P<mac_address>([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2}))',
               '(?P<state>(PERMANENT|NOARP|STALE|REACHABLE|NONE|INCOMPLETE|DELAY|PROBE|FAILED))']

    regex = re.compile('.*?'.join(x for x in regexes))
    nd_table_dict = {"neighbors": []}

    for line in nd_table.splitlines():
        data = re.search(regex, line)
        if data is not None:
            data = data.groupdict()
            data["port_id"] = data["port_id"].split()[1]

            nd_table_dict["neighbors"].append(data)

    return nd_table_dict


def _print_nd_table(nd_table):
    table_format = '{:<30} {:<20} {:<10} {}'
    print ''
    print table_format.format('IPv6 Address', 'MAC address', 'Port ID', 'State')
    
    for neighbor in nd_table["neighbors"]:
        print table_format.format(neighbor["link_local"], neighbor["mac_address"],
                                  neighbor["port_id"], neighbor["state"])

    print ''
        
        
def get_table(switch, json_output, stale, reachable):
    nd_table_json = _get_nd_table_json(switch, stale, reachable)
    
    if json_output:
        print json.dumps(nd_table_json, indent=4, sort_keys=True, separators=(',', ': '))
    else:
        _print_nd_table(nd_table_json)    