#!/usr/bin/python

import json

from ops.connection import Session

def _get_ipv6_route_table_json(switch):
    session = Session().ssh(switch)
    
    command = 'vtysh -c "show ipv6 route json"'
    route_table_json = session.send_command(command)
    return json.loads(route_table_json)


def _print_route_table(route_table_json):
    table_format = ''
    
    for route in route_table_json:
        


def get_bgp_routes_json(switch):
    pass


def get_bgp_routes(switch):
    pass
        

def get_specific_route_in_json(switch, prefix):
    pass


def get_specific_route(switch):
    pass


def get_forwarding_table_in_json(switch):
    pass


def get_forwarding_table(switch):
    pass


def get_specific_fib_route_in_json(switch, prefix):
    pass
 
    
def get_specific_fib_route(switch, prefix):
    pass


def get_route_table_in_json(switch):
    route_table_json = _get_ipv6_route_table_json(switch)
    print json.dumps(route_table_json, sort_keys=True, indent=4, separators=(',', ': '))


def get_route_table(switch):
    route_table_json = _get_ipv6_route_table_json(switch)
    


def get_route_stats_in_json(switch):
    pass


def get_route_stats(switch):
    pass