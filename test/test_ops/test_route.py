#!/usr/bin/python

import json

''' OSPF commands '''

def _get_ipv6_ospf_table_json(switch):
    command = 'vtysh -c "show ipv6 route json"'
    route_table_json = '''
{
  "fd35:1:1:1::1\/128":[
    {
      "prefix":"fd35:1:1:1::1\/128",
      "protocol":"bgp",
      "distance":200,
      "metric":20,
      "uptime":"00:13:05",
      "nexthops":[
        {
          "ip":"fd35:1:1:2::1",
          "afi":"ipv6",
          "interfaceIndex":12,
          "interfaceName":"eth1",
          "active":true
        },
        {
          "ip":"fd35:1:1:2::1",
          "afi":"ipv6",
          "interfaceIndex":12,
          "interfaceName":"eth1",
          "active":true
        }
      ]
    },
    {
      "prefix":"fd35:1:1:1::1\/128",
      "protocol":"connected",
      "nexthops":[
        {
          "fib":true,
          "directlyConnected":true,
          "interfaceIndex":66,
          "interfaceName":"eth19",
          "active":true
        }
      ]
    }
  ],
  "fd35:1:1:2::1\/128":[
    {
      "prefix":"fd35:1:1:2::1\/128",
      "protocol":"ospf6",
      "selected":true,
      "distance":110,
      "metric":20,
      "nexthops":[
        {
          "fib":true,
          "ip":"fe80::4c1:41ff:fe04:554d",
          "afi":"ipv6",
          "interfaceIndex":12,
          "interfaceName":"eth1",
          "active":true
        }
      ]
    }
  ],
  "fd35:1:1:2::16\/128":[
    {
      "prefix":"fd35:1:1:2::16\/128",
      "protocol":"ospf6",
      "selected":true,
      "distance":110,
      "metric":20,
      "nexthops":[
        {
          "fib":true,
          "ip":"fe80::b06c:59ff:fee8:b29b",
          "afi":"ipv6",
          "interfaceIndex":57,
          "interfaceName":"eth16",
          "active":true
        }
      ]
    }
  ]
}
    '''
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
    route_table_json = '''
{
  "fd35:1:1:1::1\/128":[
    {
      "prefix":"fd35:1:1:1::1\/128",
      "protocol":"bgp",
      "distance":200,
      "metric":20,
      "uptime":"00:13:05",
      "nexthops":[
        {
          "ip":"fd35:1:1:2::1",
          "afi":"ipv6",
          "interfaceIndex":12,
          "interfaceName":"eth1",
          "active":true
        },
        {
          "ip":"fd35:1:1:2::1",
          "afi":"ipv6",
          "interfaceIndex":12,
          "interfaceName":"eth1",
          "active":true
        }
      ]
    },
    {
      "prefix":"fd35:1:1:1::1\/128",
      "protocol":"connected",
      "nexthops":[
        {
          "fib":true,
          "directlyConnected":true,
          "interfaceIndex":66,
          "interfaceName":"eth19",
          "active":true
        }
      ]
    }
  ],
  "fd35:1:1:2::1\/128":[
    {
      "prefix":"fd35:1:1:2::1\/128",
      "protocol":"ospf6",
      "selected":true,
      "distance":110,
      "metric":20,
      "nexthops":[
        {
          "fib":true,
          "ip":"fe80::4c1:41ff:fe04:554d",
          "afi":"ipv6",
          "interfaceIndex":12,
          "interfaceName":"eth1",
          "active":true
        }
      ]
    }
  ],
  "fd35:1:1:2::16\/128":[
    {
      "prefix":"fd35:1:1:2::16\/128",
      "protocol":"ospf6",
      "selected":true,
      "distance":110,
      "metric":20,
      "nexthops":[
        {
          "fib":true,
          "ip":"fe80::b06c:59ff:fee8:b29b",
          "afi":"ipv6",
          "interfaceIndex":57,
          "interfaceName":"eth16",
          "active":true
        }
      ]
    }
  ]
}
    '''
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
    route_table_json = '''
{
  "fd35:1:1:1::1\/128":[
    {
      "prefix":"fd35:1:1:1::1\/128",
      "protocol":"bgp",
      "distance":200,
      "metric":20,
      "uptime":"00:13:05",
      "nexthops":[
        {
          "ip":"fd35:1:1:2::1",
          "afi":"ipv6",
          "interfaceIndex":12,
          "interfaceName":"eth1",
          "active":true
        },
        {
          "ip":"fd35:1:1:2::1",
          "afi":"ipv6",
          "interfaceIndex":12,
          "interfaceName":"eth1",
          "active":true
        }
      ]
    },
    {
      "prefix":"fd35:1:1:1::1\/128",
      "protocol":"connected",
      "nexthops":[
        {
          "fib":true,
          "directlyConnected":true,
          "interfaceIndex":66,
          "interfaceName":"eth19",
          "active":true
        }
      ]
    }
  ],
  "fd35:1:1:2::1\/128":[
    {
      "prefix":"fd35:1:1:2::1\/128",
      "protocol":"ospf6",
      "selected":true,
      "distance":110,
      "metric":20,
      "nexthops":[
        {
          "fib":true,
          "ip":"fe80::4c1:41ff:fe04:554d",
          "afi":"ipv6",
          "interfaceIndex":12,
          "interfaceName":"eth1",
          "active":true
        }
      ]
    }
  ],
  "fd35:1:1:2::16\/128":[
    {
      "prefix":"fd35:1:1:2::16\/128",
      "protocol":"ospf6",
      "selected":true,
      "distance":110,
      "metric":20,
      "nexthops":[
        {
          "fib":true,
          "ip":"fe80::b06c:59ff:fee8:b29b",
          "afi":"ipv6",
          "interfaceIndex":57,
          "interfaceName":"eth16",
          "active":true
        }
      ]
    }
  ]
}
    '''
    
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