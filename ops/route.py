#!/usr/bin/python

import json

from ops.connection import Session

def _get_ipv6_route_table_json(switch):
    session = Session().ssh(switch)
    
    command = 'vtysh -c "show ipv6 route json"'
    route_table_json = session.send_command(command)

    
''' OSPF commands '''

def get_ospf_routes_specific_entry_in_json(switch, prefix):
    pass


def get_ospf_routes_specific_entry(switch, prefix):
    pass


def get_ospf_routes_in_json(switch):
    pass


def get_ospf_routes(switch):
    pass


''' BGP commands '''

def get_bgp_routes_specific_entry_in_json(switch, prefix):
    pass


def get_bgp_routes_specific_entry(switch, prefix):
    pass


def get_bgp_routes_in_json(switch):
    pass


def get_bgp_routes(switch):
    pass


''' FIB commands '''

def get_fib_table_specific_entry_in_json(switch, prefix):
    pass
 
    
def get_fib_table_specific_entry(switch, prefix):
    pass


def get_fib_table_in_json(switch):
    pass


def get_fib_table(switch):
    pass


''' RIB commands '''

def get_rib_table_specific_entry_in_json(switch, prefix):
    pass


def get_rib_table_specific_entry(switch, prefix):
    pass


def get_rib_table_in_json(switch):
    pass


def get_rib_table(switch):
    pass