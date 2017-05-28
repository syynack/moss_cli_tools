#!/usr/bin/python

import json

from ops import log
from ops.connection import Session
from ops.connection import V6Format

def _get_ipv6_json(switch, port):
    session = Session().snmp(switch)
    
    ipv6IfDesc = [element.value for element in session.walk('.1.3.6.1.2.1.55.1.5.1.2')]
    ipv6Add = [element.oid_index for element in session.walk('.1.3.6.1.2.1.4.34.1.3.2')]
    
    del ipv6Add[0]

    addresses = {"addresses": {
                    "link_local": [],
                    "global" : [],
                    "total": {}
                    },
                }
    
    for index, address in enumerate(ipv6Add):
        if port == 0:
            if '2.16.254.128.0.0.0.0.0.0.' in address:
                addresses["addresses"]["link_local"].append({
                    "port_id": ipv6IfDesc[index].replace('"', ''),
                    "ipv6_address": V6Format(address) + "/64"
                })   
            else:
                addresses["addresses"]["global"].append({
                    "port_id": ipv6IfDesc[index].replace('"', ''),
                    "ipv6_address": V6Format(address) + "/128"
                })
        else:
            if ipv6IfDesc[index] == port:
                addresses["addresses"]["link_local"].append({
                    "port_id": ipv6IfDesc[index].replace('"', ''),
                    "ipv6_address": V6Format(address) + "/64"
                })
            if '2.16.254.128.0.0.0.0.0.0.' not in address:
                addresses["addresses"]["global"].append({
                    "port_id": ipv6IfDesc[index].replace('"', ''),
                    "ipv6_address": V6Format(address) + "/128"
                })

    addresses["addresses"]["total"]["link_local"] = len(addresses["addresses"]["link_local"])
    addresses["addresses"]["total"]["global"] = len(addresses["addresses"]["global"])
            
    return addresses


def _print_ipv6_table(ipv6_json):
    table_format = '{:<15} {:<30} {}'
    print ''
    print table_format.format('Port ID', 'Global', 'Link local')

    for address in ipv6_json["addresses"]["link_local"]: 
        print table_format.format(address["port_id"], ipv6_json["addresses"]["global"][0]["ipv6_address"],
                                  address["ipv6_address"])

    print ''
    print '  Total Link Local addresses: {}'.format(ipv6_json["addresses"]["total"]["link_local"])
    print '  Total Global addresses: {}'.format(ipv6_json["addresses"]["total"]["global"])
    print ''


def get_ports_info(switch, json_output):
    ipv6_json = _get_ipv6_json(switch, 0)

    if json_output:
        print json.dumps(ipv6_json, sort_keys=True, indent=4, separators=(',', ': '))
    else:
        _print_ipv6_table(ipv6_json)


def get_port_info(switch, json_output, port):
    ipv6_json = _get_ipv6_json(switch, port)

    if json_output:
        print json.dumps(ipv6_json, sort_keys=True, indent=4, separators=(',', ': '))
    else:
        _print_ipv6_table(ipv6_json)
    
    
def get_ports_statistics(switch, json_output):
    session = Session().snmp(switch)
    
    ipv6Forwarding = [element.value for element in session.walk('.1.3.6.1.2.1.55.1.1')]
    ipv6NumPort = [element.value for element in session.walk('.1.3.6.1.2.1.55.1.3')]

    statistics = {"statistics": {
                    "forwarding": 0,
                    "port_num": 0
                }}

    statistics["statistics"]["forwarding"] = str(ipv6Forwarding[0])
    statistics["statistics"]["port_num"] = str(ipv6NumPort[0])

    if json_output:
        print json.dumps(statistics, sort_keys=True, indent=4, separators=(',', ': '))
    else:
        print ''
        print 'Forwarding: {}\nTotal ports: {}\n'.format(statistics["statistics"]["forwarding"], 
                                                         statistics["statistics"]["port_num"])