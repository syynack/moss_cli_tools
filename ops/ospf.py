#!/usr/bin/python

import json
import re

from ops.connection import Session


def _get_ospf_neighbors_brief_json(switch):
    session = Session().ssh(switch)
    
    command = 'vtysh -c "show ipv6 ospf6 neighbor" | tail -n +2'
    output = session.send_command(command)

    output_dict = []
    regex = '(?P<neighbor_rid>([0-9]{1,3}\.){3}[0-9]{1,3})\s+(?P<priority>[^\s]+)\s+(?P<deadtime>[0-9]{2}:[0-9]{2}:[0-9]{2})\s+(?P<ospf_state>[^/]+)\/(?P<ospf_interface_state>[^\s]+)\s+(?P<uptime>[0-9]{2}:[0-9]{2}:[0-9]{2})\s(?P<interface>[^\[]+)\[(?P<interface_state>.*)]'
    
    for line in output.splitlines():
        match = re.match(regex, line)
        
        if match:
            output_dict.append(match.groupdict())
    
    return output_dict


def _print_ospf_neighbors_brief(output):
    table_format = '{:<10} {:<10} {:<10} {:<10} {:<12} {:<12} {:<22} {}'
    
    print ''
    print table_format.format('RID', 'Priority', 'Dead Time', 'Up Time', 'OSPF State', 'Interface', 'OSPF Interface State', 'State')
    
    for neighbor in output:
        print table_format.format(neighbor['neighbor_rid'], neighbor['priority'], neighbor['deadtime'], neighbor['uptime'],
            neighbor['ospf_state'], neighbor['interface'], neighbor['ospf_interface_state'], neighbor['interface_state']
        )
        
    print ''
        
        
def _get_ospf_neighbors_detail_json(switch):
    session = Session().ssh(switch)
    
    command = 'vtysh -c "show ipv6 ospf6 neighbor detail"'
    output = session.send_command(command)
 
    output_dict = {}
    regexes = ['Area\s(?P<area>[^\s]+)',
               'Link-local\saddress:\s(?P<inet6_link_local_addr>[^\s]+)',
               'State\s(?P<state>[^\s]+)\sfor\sa\sduration\sof\s(?P<uptime>[^\s]+)',
               'BDR\s(?P<remote_dr>([0-9]{1,3}\.){3}[0-9]{1,3})',
               '\/(?P<remote_bdr>([0-9]{1,3}\.){3}[0-9]{1,3})', 
               ',\sPriority\s(?P<priority>[^\s]+)',
               'BFD:\sType:\s(?P<bfd_type>[^\n]+)',
               'Detect\sMul:\s(?P<bfd_detect_multiplier>[^,]+),\sMin\sRx\sinterval:\s(?P<bfd_min_rx>[^,]+),\sMin\sTx\sinterval:\s(?P<bfd_min_tx>[^\n]+)'
              ]
    
    for line in output.splitlines():
        if 'Neighbor' in line:
            line = line.split()
            neighbor, interface = line[1].split('%')
            output_dict[neighbor] = {}
        else:
            for regex in regexes:
                match = re.search(regex, line)
                
                if match:
                    output_dict[neighbor].update(match.groupdict())
                    output_dict[neighbor].update({'interface': interface})
    
    return output_dict


def _print_ospf_neighbors_detail(output):
    table_format = '{:<15} {:<8} {:<10} {:<10} {:<10} {:<10} {:<12} {:<12} {:<12} {:<8} {}'
    
    print ''
    print table_format.format('Neighbor RID', 'State', 'Priority', 'Interface', 'Uptime', 
        'Area', 'BFD Type', 'BFD Min Rx', 'BFD Min Tx', 'BFD DM', 'Link Local Address'
    )
    
    for neighbor in output:
        print table_format.format(neighbor, output[neighbor]['state'], output[neighbor]['priority'], output[neighbor]['interface'],
            output[neighbor]['uptime'], output[neighbor]['area'], output[neighbor]['bfd_type'], output[neighbor]['bfd_min_rx'],
            output[neighbor]['bfd_min_tx'], output[neighbor]['bfd_detect_multiplier'], output[neighbor]['inet6_link_local_addr']
        )
        
    print ''


def _get_ospf_interfaces_json(switch):
    session = Session().ssh(switch)
    
    command = 'vtysh -c "show ipv6 ospf6 interface"'
    output = session.send_command(command)
    
    output_dict = {}
    regexes = ['[^\s]+\sis\sup,\stype\s(?P<type>[^\n]+)',
               'inet6:\s(?P<inet6_addr>[^\n]+)',
               'Area\sID\s(?P<area>([0-9]{1,3}\.){3}[0-9]{1,3}),\sCost\s(?P<cost>[^\n]+)',
               'State\s(?P<state>[^,]+),\s.*,\sPriority\s(?P<priority>[^\n]+)',
               'Hello\s(?P<hello_time>[^,]+),\sDead\s(?P<dead_time>[^,]+),\sRetransmit\s(?P<retrans_time>[^\n])',
               'DR:\s(?P<dr>([0-9]{1,3}\.){3}[0-9]{1,3})\sBDR:\s(?P<bdr>([0-9]{1,3}\.){3}[0-9]{1,3})',
               'Detect\sMul:\s(?P<bfd_detect_multiplier>[^,]+),\sMin\sRx\sinterval:\s(?P<bfd_min_rx>[^,]+),\sMin\sTx\sinterval:\s(?P<bfd_min_tx>[^\n]+)'
              ]
    
    for line in output.splitlines():
        if 'is up, type' in line:
            line = line.split()
            interface = line[0]
            output_dict[interface] = {}
        else:    
            for regex in regexes:
                match = re.search(regex, line)
            
                if match:
                    if 'inet6' in line:
                        cur_address = output_dict[interface].get('inet6_addr')
                        output_dict[interface]['inet6_addr'] = []
                        
                        if cur_address is not None:
                            output_dict[interface]['inet6_addr'].append(cur_address[0])
                        
                        result = match.groupdict()
                        output_dict[interface]['inet6_addr'].append(result['inet6_addr'])
                    else:
                        output_dict[interface].update(match.groupdict())
                    
    return output_dict


def _print_ospf_interfaces(output):
    table_format = '{:<10} {:<10} {:<7} {:<10} {:<12} {:<12} {:<14} {:<14} {:<30} {:<11} {:<11} {}'
    
    print ''
    print table_format.format('Port ID', 'Area', 'Cost', 'Priority', 'Hello Time', 
        'Dead Time', 'Retrans Time', 'State', 'Addresses', 'BFD Min Rx', 'BFD Min Tx', 'BFD DM'
    )
    
    for interface in output:
        if 'area' in output[interface]:
            print table_format.format(interface, output[interface]['area'], output[interface]['cost'], output[interface]['priority'],
                output[interface]['hello_time'], output[interface]['dead_time'], output[interface]['retrans_time'], output[interface]['state'],
                output[interface]['inet6_addr'][0], output[interface]['bfd_min_rx'], output[interface]['bfd_min_tx'], 
                output[interface]['bfd_detect_multiplier']
            )
            
            if len(output[interface]['inet6_addr']) > 1:
                addr_count = 1
                for address in output[interface]['inet6_addr'][1:]:
                    print table_format.format('', '', '', '', '', '', '', '', output[interface]['inet6_addr'][addr_count], '', '', '')
                    
            print ''
                
    print ''
            

def get_ospf_neighbors_brief_specific_neighbor_in_json(switch, neighbor):
    output = _get_ospf_neighbors_brief_json(switch)
    input = []
    
    for entry in output:
        if entry['neighbor_rid'] == neighbor:
            input.append(entry)
         
    print json.dumps(input, sort_keys=True, indent=4, separators=(',', ': '))


def get_ospf_neighbors_brief_in_json(switch):
    output = _get_ospf_neighbors_brief_json(switch)
    print json.dumps(output, sort_keys=True, indent=4, separators=(',', ': '))


def get_ospf_neighbors_brief_specific_neighbor(switch, neighbor):
    output = _get_ospf_neighbors_brief_json(switch)
    input = []
    
    for entry in output:
        if entry['neighbor_rid'] == neighbor:
            input.append(entry)
         
    _print_ospf_neighbors_brief(input)


def get_ospf_neighbors_brief(switch):
    output = _get_ospf_neighbors_brief_json(switch)
    _print_ospf_neighbors_brief(output)


def get_ospf_neighbors_detail_specific_neighbor_in_json(switch, neighbor):
    output = _get_ospf_neighbors_detail_json(switch)
    input = {}
    
    for entry in output:
        if entry == neighbor:
            input[entry] = {}
            input[entry].update(output[entry])
         
    print json.dumps(input, sort_keys=True, indent=4, separators=(',', ': '))


def get_ospf_neighbors_detail_in_json(switch):
    output = _get_ospf_neighbors_detail_json(switch)
    print json.dumps(output, sort_keys=True, indent=4, separators=(',', ': '))
    

def get_ospf_neighbors_detail_specific_neighbor(switch, neighbor):
    output = _get_ospf_neighbors_detail_json(switch)
    input = {}
    
    for entry in output:
        if entry == neighbor:
            input[entry] = {}
            input[entry].update(output[entry])
         
    _print_ospf_neighbors_detail(input)


def get_ospf_neighbors_detail(switch):
    output = _get_ospf_neighbors_detail_json(switch)
    _print_ospf_neighbors_detail(output)


def get_ospf_interfaces_specific_interface_in_json(switch, int):
    output = _get_ospf_interfaces_json(switch)
    input = {}
    
    for entry in output:
        if entry == int:
            input[entry] = {}
            input[entry].update(output[entry])
         
    print json.dumps(input, sort_keys=True, indent=4, separators=(',', ': '))


def get_ospf_interfaces_in_json(switch):
    output = _get_ospf_interfaces_json(switch)
    print json.dumps(output, sort_keys=True, indent=4, separators=(',', ': '))


def get_ospf_interfaces_specific_interface(switch, int):
    output = _get_ospf_interfaces_json(switch)
    input = {}
    
    for entry in output:
        if entry == int:
            input[entry] = {}
            input[entry].update(output[entry])
         
    _print_ospf_interfaces(input)
    

def get_ospf_interfaces(switch):
    output = _get_ospf_interfaces_json(switch)
    _print_ospf_interfaces(output)