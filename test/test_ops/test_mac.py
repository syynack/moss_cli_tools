#!/usr/bin/python

import json
import re

from test_ops import test_log

def _get_macs_json(switch):    
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
    output = _get_macs_json(switch)
        
    _print_macs_table(output)
        
        
def get_interface_mac_addresses_in_json(switch):
    output = _get_macs_json(switch)

    print json.dumps(output, sort_keys=True, indent=4, separators=(',', ': '))