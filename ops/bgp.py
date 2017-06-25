#!/usr/bin/python

import json

from ops import utils
from ops.connection import Session


def _get_bgp_memory_json(switch):
    session = Session().ssh(switch)
    
    command = 'vtysh -c "show bgp memory"'
    bgp_memory_output = session.send_command(command)
    bgp_memory_json = {"tables": []}
    
    for line in bgp_memory_output.splitlines():
        line = line.split(',')
        
        if len(line) > 1:
            table_details = line[0].split()
            memory_usage = line[1].split()
            
            if memory_usage[3] == 'KiB':
                memory_usage[2] = int(memory_usage[2]) * 1024
            
            bgp_memory_json["tables"].append({
                "table_id": '_'.join(table_details[1:]).lower().replace('-', '_'),
                "total": table_details[0],
                "mem_usage": str(memory_usage[2])
            })
        
    return bgp_memory_json


def _get_bgp_neighbors_json(switch):
    session = Session().ssh(switch)
    
    command = 'vtysh -c "show bgp neighbors json"'
    bgp_neighbors_json = session.send_command(command)
    
    return json.load(bgp_neighbors_json)


def _print_bgp_neighbor(bgp_neighbors_json, peer):
    if bgp_neighbors_json[peer]["bgpState"] == 'Established':
        print utils.get_bgp_neighbor_established(bgp_neighbors_json, peer)
    else:
        print utils.get_bgp_neighbor_not_established(bgp_neighbors_json, peer)
    
    
def _get_bgp_summary_json(switch):
    session = Session().ssh(switch)
    
    command = 'vtysh -c "show bgp summary json"'
    bgp_summary_json = session.send_command(command)
    return bgp_summary_json


def get_bgp_memory_usage_in_json(switch):
    bgp_memory_json = _get_bgp_memory_json(switch)
    print json.dumps(bgp_memory_json, sort_keys=True, indent=4, separators=(',', ': '))


def get_bgp_memory_usage(switch):
    bgp_memory_json = _get_bgp_memory_json(switch)
    
    table_format = '{:<25} {:<18} {}'
    print table_format.format('Table ID', 'Total Entries', 'Memory Usage (Bytes)')
    
    for table in bgp_memory_json["tables"]:
        print table_format.format(table["table_id"], table["total"], table["mem_usage"])
        

def get_bgp_specific_neighbor_in_json(switch, neighbor):
    bgp_neighbors_json = _get_bgp_neighbors_json(switch)
    input = {}
    
    for peer in bgp_neighbors_json:
        if peer == neighbor:
            input[neighbor] = bgp_neighbors_json[peer]
            
    print json.dumps(input, sort_keys=True, indent=4, separators=(',', ': '))
    

def get_bgp_specific_neighbor(switch, neighbor):
    bgp_neighbors_json = _get_bgp_neighbors_json(switch)
    
    for peer in bgp_neighbors_json:
        if peer == neighbor:
            _print_bgp_neighbor(bgp_neighbors_json, peer)


def get_bgp_neighbors_in_json(switch):
    bgp_neighbors_json = _get_bgp_neighbors_json(switch)
    print json.dumps(bgp_neighbors_json, sort_keys=True, indent=4, separators=(',', ': '))


def get_bgp_neighbors(switch):
    bgp_neighbors_json = _get_bgp_neighbors_json(switch)
    
    for peer in bgp_neighbors_json:
        _print_bgp_neighbor(bgp_neighbors_json, peer)


def get_bgp_summary_in_json(switch):
    bgp_summary_json = json.loads(_get_bgp_summary_json(switch))
    print json.dumps(bgp_summary_json, sort_keys=True, indent=4, separators=(',', ': '))
    

def get_bgp_summary(switch):
    bgp_summary_json = json.loads(_get_bgp_summary_json(switch))
    
    print ''
    print '  Local Router ID: {}'.format(bgp_summary_json.get('routerId'))
    print ''
    
    table_format = '{:<20} {:<20} {:<12} {:<12} {:<8} {:<4} {:<8} {:<8} {:<8} {:<10} {:<10} {:<8} {}'
    print table_format.format('IPv6 Address', 'Hostname', 'State', 'Remote AS', 'Type', 'V', 'msgRecv', 'msgSent',
                              'Table V', 'UP/DOWN', 'Prefixes', 'inQ', 'outQ')
    
    for peer in bgp_summary_json["peers"]:
        print table_format.format(peer, bgp_summary_json["peers"][peer].get('hostname'), 
                                  bgp_summary_json["peers"][peer]["state"], bgp_summary_json["peers"][peer]["remoteAs"],
                                  bgp_summary_json["peers"][peer]["idType"], bgp_summary_json["peers"][peer]["version"],
                                  bgp_summary_json["peers"][peer]["msgRcvd"], bgp_summary_json["peers"][peer]["msgSent"],
                                  bgp_summary_json["peers"][peer]["tableVersion"],
                                  bgp_summary_json["peers"][peer]["peerUptime"],
                                  bgp_summary_json["peers"][peer]["prefixReceivedCount"],
                                  bgp_summary_json["peers"][peer]["inq"], bgp_summary_json["peers"][peer]["outq"])
    
    print ''
    print '  RIB Count: {}'.format(bgp_summary_json.get("ribCount"))
    print '  RIB Memory: {}'.format(bgp_summary_json.get("ribMemory"))
    print '  Total peers: {}'.format(bgp_summary_json.get("totalPeers"))
    print ''