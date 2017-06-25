#!/usr/bin/python

import json

from ops.connection import Session

    
''' OSPF commands '''

def _get_ipv6_ospf_table_json(switch):
    session = Session().ssh(switch)
    
    command = 'vtysh -c "show ipv6 route json"'
    route_table_json = session.send_command(command)
    route_table_json = json.loads(route_table_json)
    
    output = {}
    subroute_count = 0
    
    for route in route_table_json:
        for subroute in route_table_json[route]:
            if route_table_json[route][subroute_count]['protocol'] == 'ospf6':
                output[route] = route_table_json[route][subroute_count]
                
    return output


def _print_ospf_table(output):
    table_format = '{:<20} {:<12} {:<10} {:<8} {:<5} {}'
    
    print ''
    print table_format.format('Prefix', 'Protocol', 'Selected', 'Active', 'FIB', 'Interface Name')
    
    for prefix in output:
        print table_format.format(prefix, output[prefix]['protocol'], output[prefix].get('selected'),
            output[prefix]['nexthops'][0].get('active'), output[prefix]['nexthops'][0].get('fib'),
            output[prefix]['nexthops'][0].get('interfaceName')
        )
            
    print ''
    

def get_ospf_routes_specific_entry_in_json(switch, prefix):
    output = _get_ipv6_ospf_table_json(switch)
    input = {}
    
    for route in output:
        if prefix in route:
            input[route] = output[route]
            
    print json.dumps(input, sort_keys=True, indent=4, separators=(',', ': '))


def get_ospf_routes_specific_entry(switch, prefix):
    output = _get_ipv6_ospf_table_json(switch)
    input = {}
    
    for route in output:
        if prefix in route:
            input[route] = output[route]
            
    _print_ospf_table(input)


def get_ospf_routes_in_json(switch):
    output = _get_ipv6_ospf_table_json(switch)
    print json.dumps(output, sort_keys=True, indent=4, separators=(',', ': '))


def get_ospf_routes(switch):
    output = _get_ipv6_ospf_table_json(switch)
    _print_ospf_table(output)


''' BGP commands '''

def _get_ipv6_bgp_table_json(switch):
    session = Session().ssh(switch)
    
    command = 'vtysh -c "show ipv6 route json"'
    route_table_json = session.send_command(command)
    route_table_json = json.loads(route_table_json)
    
    output = {}
    subroute_count = 0
    
    for route in route_table_json:
        for subroute in route_table_json[route]:
            if route_table_json[route][subroute_count]['protocol'] == 'bgp':
                output[route] = route_table_json[route][subroute_count]
                
    return output


def _print_bgp_table(output):
    table_format = '{:<20} {:<12} {:<10} {:<8} {:<5} {}'
    
    print ''
    print table_format.format('Prefix', 'Protocol', 'Selected', 'Active', 'FIB', 'Interface Name')
    
    for prefix in output:
        print table_format.format(prefix, output[prefix]['protocol'], output[prefix].get('selected'),
            output[prefix]['nexthops'][0].get('active'), output[prefix]['nexthops'][0].get('fib'),
            output[prefix]['nexthops'][0].get('interfaceName')
        )
            
    print ''
    

def get_bgp_routes_specific_entry_in_json(switch, prefix):
    output = _get_ipv6_bgp_table_json(switch)
    input = {}
    
    for route in output:
        if prefix in route:
            input[route] = output[route]
            
    print json.dumps(input, sort_keys=True, indent=4, separators=(',', ': '))


def get_bgp_routes_specific_entry(switch, prefix):
    output = _get_ipv6_bgp_table_json(switch)
    input = {}
    
    for route in output:
        if prefix in route:
            input[route] = output[route]
            
    _print_bgp_table(input)


def get_bgp_routes_in_json(switch):
    output = _get_ipv6_bgp_table_json(switch)
    print json.dumps(output, sort_keys=True, indent=4, separators=(',', ': '))


def get_bgp_routes(switch):
    output = _get_ipv6_bgp_table_json(switch)
    _print_bgp_table(output)

''' RIB commands '''

def _get_ipv6_rib_table_json(switch):
    session = Session().ssh(switch)
    
    command = 'vtysh -c "show ipv6 route json"'
    route_table_json = session.send_command(command)
    
    return json.loads(route_table_json)


def _print_rib_table(output):
    table_format = '{:<20} {:<12} {:<10} {:<8} {:<5} {}'
    
    print ''
    print table_format.format('Prefix', 'Protocol', 'Selected', 'Active', 'FIB', 'Interface Name')
    
    for prefix in output:
        count = 0
        
        for subroute in output[prefix]:
            print table_format.format(prefix, output[prefix][count]['protocol'], output[prefix][count].get('selected'),
                output[prefix][count]['nexthops'][0].get('active'), output[prefix][count]['nexthops'][0].get('fib'),
                output[prefix][count]['nexthops'][0].get('interfaceName')
            )
            
            count += 1
            
    print ''


def get_rib_table_specific_entry_in_json(switch, prefix):
    output = _get_ipv6_rib_table_json(switch)
    input = {}
    
    for route in output:
        if prefix in route:
            input[route] = output[route]
            
    print json.dumps(input, sort_keys=True, indent=4, separators=(',', ': '))
        

def get_rib_table_specific_entry(switch, prefix):
    output = _get_ipv6_rib_table_json(switch)
    input = {}
    
    for route in output:
        if prefix in route:
            input[route] = output[route]
            
    _print_rib_table(input)


def get_rib_table_in_json(switch):
    output = _get_ipv6_rib_table_json(switch)
    print json.dumps(output, sort_keys=True, indent=4, separators=(',', ': '))


def get_rib_table(switch):
    output = _get_ipv6_rib_table_json(switch)
    _print_rib_table(output)