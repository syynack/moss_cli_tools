#!/usr/bin/python

import json
import re

from test_ops import test_log
from test_ops import test_ipv6

def _get_interfaces_json(switch):
    ipv6_addr_dict = test_ipv6._get_ipv6_json(switch)
    command = 'vtysh -c "show interface description" | tail -n +2'
    output = '''
eth0            up      up        
eth1            up      up        d1-p1-l1-r1 eth1 <> d1-p1-l2-r1 eth1
eth2            up      up        d1-p1-l1-r1 eth2 <> d1-p1-l2-r2 eth1
eth3            up      up        d1-p1-l1-r1 eth3 <> d1-p1-l2-r3 eth1
eth4            up      up        d1-p1-l1-r1 eth4 <> d1-p1-l2-r4 eth1
eth5            up      up        d1-p1-l1-r1 eth5 <> d1-p1-l2-r5 eth1
eth6            up      up        d1-p1-l1-r1 eth6 <> d1-p1-l2-r6 eth1
eth7            up      up        d1-p1-l1-r1 eth7 <> d1-p1-l2-r7 eth1
eth8            up      up        d1-p1-l1-r1 eth8 <> d1-p1-l2-r8 eth1
eth9            up      up        d1-p1-l1-r1 eth9 <> d1-p1-l2-r9 eth1
eth10           up      up        d1-p1-l1-r1 eth10 <> d1-p1-l2-r10 eth1
eth11           up      up        d1-p1-l1-r1 eth11 <> d1-p1-l2-r11 eth1
eth12           up      up        d1-p1-l1-r1 eth12 <> d1-p1-l2-r12 eth1
eth13           up      up        d1-p1-l1-r1 eth13 <> d1-p1-l2-r13 eth1
eth14           up      up        d1-p1-l1-r1 eth14 <> d1-p1-l2-r14 eth1
eth15           up      up        d1-p1-l1-r1 eth15 <> d1-p1-l2-r15 eth1
eth16           up      up        d1-p1-l1-r1 eth16 <> d1-p1-l2-r16 eth1
eth17           up      up        TOR facing port
eth18           up      up        TOR facing port
eth19           up      up        TOR facing port
eth20           up      up        TOR facing port
eth21           up      up        TOR facing port
eth22           up      up        TOR facing port
eth23           up      up        TOR facing port
eth24           up      up        TOR facing port
eth25           up      up        TOR facing port
eth26           up      up        TOR facing port
eth27           up      up        TOR facing port
eth28           up      up        TOR facing port
eth29           up      up        TOR facing port
eth30           up      up        TOR facing port
eth31           up      up        TOR facing port
eth32           up      up        TOR facing port
lo              up      up        
    '''
    
    output_dict = {}
    
    for line in output.splitlines():
        line = line.split()
        
        if len(line) > 0:
            output_dict[line[0]] = {
                "admin_status": line[1],
                "line_status": line[2],
                "description": "" if len(line) < 4 else ' '.join(line[3:]),
                "ipv6_addr": "" if line[0] not in ipv6_addr_dict else ipv6_addr_dict[line[0]][0]
            }
        
    return output_dict


def _get_interfaces_detail_json(switch):
    command = 'ifconfig'
    output = '''
eth1      Link encap:Ethernet  HWaddr 02:42:ac:11:00:02
          inet addr:172.17.0.2  Bcast:0.0.0.0  Mask:255.255.0.0
          inet6 addr: fe80::42:acff:fe11:2/64 Scope:Link
          inet6 addr: fd35:1:1:1::1/128 Scope:Global
          UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
          RX packets:18695 errors:0 dropped:0 overruns:0 frame:0
          TX packets:16425 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:0
          RX bytes:1811497 (1.7 MiB)  TX bytes:2945293 (2.8 MiB)

lo        Link encap:Local Loopback
          inet addr:127.0.0.1  Mask:255.0.0.0
          inet6 addr: ::1/128 Scope:Host
          UP LOOPBACK RUNNING  MTU:65536  Metric:1
          RX packets:0 errors:0 dropped:0 overruns:0 frame:0
          TX packets:0 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:1
          RX bytes:0 (0.0 B)  TX bytes:0 (0.0 B)
    '''
    
    output_dict = {}
    regexes = ['Link encap:(?P<link_encapsulation>[^\s]+)', 
               'MTU:(?P<mtu>[^\s]+)',
               'RX\spackets:(?P<rx_ok>[^\s]+)\serrors:(?P<rx_err>[^\s]+)\sdropped:(?P<rx_drp>[^\s]+)\soverruns:(?P<rx_ovr>[^\s]+)\sframe:(?P<rx_frm>[^\s]+)',
               'TX\spackets:(?P<tx_ok>[^\s]+)\serrors:(?P<tx_err>[^\s]+)\sdropped:(?P<tx_drp>[^\s]+)\soverruns:(?P<tx_ovr>[^\s]+)\scarrier:(?P<tx_car>[^\s]+)',
               'collisions:(?P<collisions>[^\s]+)\stxqueuelen:(?P<tx_queue_length>[^\s]+)',
               'RX\sbytes:(?P<rx_bytes>[^\s]+)\s\(((?P<rx_total>[^)]+))\)',
               'TX\sbytes:(?P<tx_bytes>[^\s]+)\s\(((?P<tx_total>[^)]+))\)'
              ]
    
    for line in output.splitlines():
        
        if 'Link encap' in line:
            split_line = line.split()
            port_id = split_line[0]
            output_dict[port_id] = {}
        
        for regex in regexes:
            match = re.search(regex, line)
            
            if match:
                output_dict[port_id].update(match.groupdict())
        
    return output_dict


def _print_interfaces_brief(interfaces_json):
    table_format = '{:<15} {:<15} {:<15} {}'
    
    print ''
    print table_format.format('Port ID', 'Admin Status', 'Line Status', 'Address')
    
    for interface in sorted(interfaces_json):
        print table_format.format(
            interface, interfaces_json[interface]["admin_status"],
            interfaces_json[interface]["line_status"],
            interfaces_json[interface]["ipv6_addr"]
        )
        
        if len(interfaces_json[interface]["ipv6_addr"]) > 1 and type(interfaces_json[interface]["ipv6_addr"]) == 'list':
            for address in interfaces_json[interface]["ipv6_addr"][1:]:
                print table_format.format(
                    '', '', '', address
                )
                
    print ''
    
    
def _print_interfaces_descriptions(interfaces_json):
    table_format = '{:<15} {:<15} {:<15} {}'
    
    print ''
    print table_format.format('Port ID', 'Admin Status', 'Line Status', 'Description')
    
    for interface in sorted(interfaces_json):
        print table_format.format(
            interface, interfaces_json[interface]["admin_status"],
            interfaces_json[interface]["line_status"],
            interfaces_json[interface]["description"]
        )
                
    print ''
    
    
def _print_interfaces_detail(interfaces_json):
    table_format = '{:<10} {:<8} {:<8} {:<8} {:<8} {:<8} {:<10} {:<10} {:<8} {:<8} {:<8} {:<8} {:<8} {:<10} {:<12} {:<12} {}'
    
    print ''
    print table_format.format('Port ID', 'tx_ok', 'tx_err', 'tx_drp', 'tx_ovr', 
        'tx_car', 'tx Bytes', 'tx Total', 'rx_ok', 'rx_err', 'rx_drp', 'rx_ovr', 
        'rx_frm', 'rx Bytes', 'rx Total', 'Collisions', 'Link Encapsulation')
    
    for interface in interfaces_json:
        print table_format.format(interface, interfaces_json[interface]["tx_ok"], interfaces_json[interface]["tx_err"],
            interfaces_json[interface]["tx_drp"], interfaces_json[interface]["tx_ovr"], interfaces_json[interface]["tx_car"],
            interfaces_json[interface]["tx_bytes"], interfaces_json[interface]["tx_total"], interfaces_json[interface]["rx_ok"],
            interfaces_json[interface]["rx_err"], interfaces_json[interface]["rx_drp"], interfaces_json[interface]["rx_ovr"],
            interfaces_json[interface]["rx_frm"], interfaces_json[interface]["rx_bytes"], interfaces_json[interface]["rx_total"],
            interfaces_json[interface]["collisions"], interfaces_json[interface]["link_encapsulation"]
        )
        
    print ''
    
    
def get_interfaces_brief_for_specific_interface_in_json(switch, int):
    output = _get_interfaces_json(switch)
    input = {}
    
    for interface in output:
        if interface == int:
            input[interface] = output[interface]
            del input[interface]["description"]
            
    print json.dumps(input, sort_keys=True, indent=4, separators=(',', ': '))


def get_interfaces_brief_for_specific_interface(switch, int):
    output = _get_interfaces_json(switch)
    input = {}
    
    for interface in output:
        if interface == int:
            input[interface] = output[interface]
            del input[interface]["description"]
         
    _print_interfaces_brief(input)


def get_interfaces_brief_in_json(switch):
    output = _get_interfaces_json(switch)
    
    for interface in output:
        del output[interface]["description"]
    
    print json.dumps(output, sort_keys=True, indent=4, separators=(',', ': '))


def get_interfaces_brief(switch):
    output = _get_interfaces_json(switch)
    _print_interfaces_brief(output)
    
    
def get_interfaces_descriptions_for_specific_interface_in_json(switch, int):
    output = _get_interfaces_json(switch)
    input = {}
    
    for interface in output:
        if interface == int:
            input[interface] = output[interface]
            del input[interface]["ipv6_addr"]
            
    print json.dumps(input, sort_keys=True, indent=4, separators=(',', ': '))


def get_interfaces_descriptions_for_specific_interface(switch, int):
    output = _get_interfaces_json(switch)
    input = {}
    
    for interface in output:
        if interface == int:
            input[interface] = output[interface]
            del input[interface]["ipv6_addr"]
         
    _print_interfaces_descriptions(input)


def get_interfaces_descriptions_in_json(switch):
    output = _get_interfaces_json(switch)
    
    for interface in output:
        del output[interface]["ipv6_addr"]
    
    print json.dumps(output, sort_keys=True, indent=4, separators=(',', ': '))


def get_interfaces_descriptions(switch):
    output = _get_interfaces_json(switch)
    _print_interfaces_descriptions(output)


def get_interfaces_detail_for_specific_interface_in_json(switch, int):
    output = _get_interfaces_detail_json(switch)
    input = {}
    
    for interface in output:
        if interface == int:
            input[interface] = output[interface]
    
    print json.dumps(input, sort_keys=True, indent=4, separators=(',', ': '))


def get_interfaces_detail_for_specific_interface(switch, int):
    output = _get_interfaces_detail_json(switch)
    input = {}
    
    for interface in output:
        if interface == int:
            input[interface] = output[interface]
         
    _print_interfaces_detail(input)


def get_interfaces_detail_in_json(switch):
    output = _get_interfaces_detail_json(switch)
    
    print json.dumps(output, sort_keys=True, indent=4, separators=(',', ': '))


def get_interfaces_detail(switch):
    output = _get_interfaces_detail_json(switch)
    _print_interfaces_detail(output)