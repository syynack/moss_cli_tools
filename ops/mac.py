#!/usr/bin/python

import json

from ops.connection import Session
from ops import log


def _get_macs_json(switch, _port):
    session = Session().snmp(switch)
    ifDesc = [element.value for element in session.walk('.1.3.6.1.2.1.55.1.5.1.2')]
    macAddr = [element.value for element in session.walk('.1.3.6.1.2.1.2.2.1.6')]
    
    macs = {"mac_addresses": []}
    macs_count = 0

    for index, port in enumerate(ifDesc):
        if _port == 0:
            macs["mac_addresses"].append({
                "port_id": port.replace('"', ''),
                "ll_addr": macAddr[index]
            })
        else:
            if port == _port:
                macs["mac_addresses"].append({
                    "port_id": port.replace('"', ''),
                    "ll_addr": macAddr[index]
                })

    return macs


def _print_macs_table(macs_json):
    table_format = '{:<15} {}'
    macs_count = 0

    print ''
    print table_format.format('Port ID', 'MAC address')
        
    for mac in macs_json["mac_addresses"]:
        macs_count += 1
        print table_format.format(mac["port_id"], mac["ll_addr"])
            
    print ''
    print '  Total MACs: {}'.format(macs_count)
    print ''


def get_macs(switch, json_output):
    macs_json = _get_macs_json(switch, 0)
        
    if json_output:
        log.debug('JSON formatted')
        print json.dumps(macs_json, sort_keys=True, indent=4, separators=(',', ': '))
    else:
        _print_macs_table(macs_json)
    

def get_mac_for_port(switch, json_output, _port):
    macs_json = _get_macs_json(switch, _port)
        
    if json_output:
        log.debug('JSON formatted')
        print json.dumps(macs_json, sort_keys=True, indent=4, separators=(',', ': '))
    else:
        _print_macs_table(macs_json)