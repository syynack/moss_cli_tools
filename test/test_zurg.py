#!/usr/bin/python

import click

from test_ops import test_bgp as bgp
from test_ops import test_ospf as ospf
from test_ops import test_interface as interface
from test_ops import test_ipv6 as ipv6
from test_ops import test_lldp as lldp
from test_ops import test_mac as mac
from test_ops import test_nd as nd 
from test_ops import test_route as route
from test_ops import test_system as system


class BgpCommands(object):
    ''' BGP commands '''

    @click.group(help='Display BGP information')
    def bgp():
        pass
    
    
    @click.command(help='Show the current BGP table memory usage')
    @click.option('-j', '--json', is_flag=True, help='Output in JSON format')
    @click.pass_obj
    def _memory(switch, json): # show bgp memory
        if json:
            bgp.get_bgp_memory_usage_in_json(switch.switch)
        else:
            bgp.get_bgp_memory_usage(switch.switch)
    
    
    @click.command(help='Show information about BGP neighbors')
    @click.option('-n', '--neighbor', default='', help='Show information for a specific peer')
    @click.option('-j', '--json', is_flag=True, help='Output in JSON format')
    @click.pass_obj
    def _neighbors(switch, neighbor, json):
        if neighbor and json:
            bgp.get_bgp_specific_neighbor_in_json(switch.switch, neighbor)
        elif neighbor:
            bgp.get_bgp_specific_neighbor(switch.switch, neighbor)
        elif json:
            bgp.get_bgp_neighbors_in_json(switch.switch)
        else:
            bgp.get_bgp_neighbors(switch.switch)
    
    
    @click.command(help='Show summary of BGP peers')
    @click.option('-j', '--json', is_flag=True, help='Output in JSON format')
    @click.pass_obj
    def _summary(switch, json): # show bgp summary
        if json:
            bgp.get_bgp_summary_in_json(switch.switch)
        else:
            bgp.get_bgp_summary(switch.switch)
    
    
    bgp.add_command(_memory, name='memory')
    bgp.add_command(_neighbors, name='neighbors')
    bgp.add_command(_summary, name='summary')
    

class ConfCommands(object):
    ''' Config commands '''

    @click.command(help='Show the running configuration')
    @click.option('-df', '--diff-file', default='', help='Diff the current running config against config file')
    @click.option('-ds', '--diff-switch', default='', help='Diff -s switch running config against other switch')
    @click.option('-o', '--output-file', default='', help='Filename to output config to')
    @click.pass_obj
    def running_config(switch, diff_file, diff_switch, output_file):
        if not diff_file and not diff_switch:
            config.get_running_config(switch.switch, output_file)
        elif diff_file:
            config.diff_config_file(switch.switch, diff_file, output_file)
        elif diff_switch:
            config.diff_config_switch(switch.switch, diff_switch, output_file)

 
class Ipv6Commands(object):
    ''' IPv6 commands '''

    @click.group(help='Show IPv6 information')
    def ipv6():
        pass
    

    @click.command(help='Show IPv6 info for a port')
    @click.option('-j', '--json', is_flag=True, help='Output in JSON format')
    @click.pass_obj
    def _addresses(switch, json):
        if json:
            ipv6.get_ipv6_addresses_in_json(switch.switch)
        else:
            ipv6.get_ipv6_addresses(switch.switch)
           

    ipv6.add_command(_addresses, name='addresses')


class LldpCommands(object):
    ''' LLDP commands '''

    @click.group(help='Show LLDP information')
    def lldp():
        pass


    @click.command(help='Show LLDP neighbors')
    @click.option('-j', '--json', is_flag=True, help='Output in JSON format')
    @click.option('-i', '--int', default='', help='Show LLDP neighbor for an interface')
    @click.pass_obj
    def _neighbors(switch, json, int):
        if json:
            if int:
                lldp.get_lldp_neighbors_for_specific_interface_in_json(switch.switch, int)
            else:
                lldp.get_lldp_neighbors_in_json(switch.switch)
        else:
            if int:
                lldp.get_lldp_neighbors_for_specific_interface(switch.switch, int)
            else:
                lldp.get_lldp_nighbors(switch.switch)


    lldp.add_command(_neighbors, name='neighbors')


class MacCommands(object):
    ''' MAC commands '''

    @click.command(help='Show MAC information')
    @click.option('-j', '--json', is_flag=True, help='Output in JSON format')
    @click.pass_obj
    def mac(switch, json):
        if json:
            mac.get_interface_mac_addresses_in_json(switch.switch)
        else:
            mac.get_interface_mac_addresses(switch.switch)
            
            
class OspfCommands():
    
    @click.group(help='Show OSPFv3 information')
    def ospf():
        pass
    
    
    @click.command(help='Show OSPFv3 brief neighbor information')
    @click.option('-j', '--json', is_flag=True, help='Output in JSON format')
    @click.option('-n', '--neighbor', default='', help='Show specific neighbor')
    @click.pass_obj
    def _brief(switch, json, neighbor):
        if json:
            if neighbor != '':
                ospf.get_ospf_neighbors_brief_specific_neighbor_in_json(switch.switch, neighbor)
            else:
                ospf.get_ospf_neighbors_brief_in_json(switch.switch)
        else:
            if neighbor != '':
                ospf.get_ospf_neighbors_brief_specific_neighbor(switch.switch, neighbor)
            else:
                ospf.get_ospf_neighbors_brief(switch.switch)
            
            
    @click.command(help='Show OSPFv3 detailed neighbor information')
    @click.option('-j', '--json', is_flag=True, help='Output in JSON format')
    @click.option('-n', '--neighbor', default='', help='Show specific neighbor')
    @click.pass_obj
    def _detail(switch, json, neighbor):
        if json:
            if neighbor != '':
                ospf.get_ospf_neighbors_detail_specific_neighbor_in_json(switch.switch, neighbor)
            else:
                ospf.get_ospf_neighbors_detail_in_json(switch.switch)
        else:
            if neighbor != '':
                ospf.get_ospf_neighbors_detail_specific_neighbor(switch.switch, neighbor)
            else:
                ospf.get_ospf_neighbors_detail(switch.switch)
    
    
    @click.command(help='Show OSPFv3 interface information')
    @click.option('-j', '--json', is_flag=True, help='Output in JSON format')
    @click.option('-i', '--int', default='', help='Show specific interface')
    @click.pass_obj
    def _interface(switch, json, int):
        if json:
            if int:
                ospf.get_ospf_interfaces_specific_interface_in_json(switch.switch, int)
            else:
                ospf.get_ospf_interfaces_in_json(switch.switch)
        else:
            if int:
                ospf.get_ospf_interfaces_specific_interface(switch.switch, int)
            else:
                ospf.get_ospf_interfaces(switch.switch)
                
                
    ospf.add_command(_brief, name='brief')
    ospf.add_command(_detail, name='detail')
    ospf.add_command(_interface, name='interfaces')
            
          
class NdCommands(object):
    ''' ND IPv6 commands '''
    
    @click.command(help='Show IPv6 Neighbor Discovery table')
    @click.option('-j', '--json', is_flag=True, help='Output in JSON format')
    @click.option('-s', '--stale', is_flag=True, help='Show only stale neighbors')
    @click.option('-r', '--reachable', is_flag=True, help='Show only reachable neighbors')
    @click.pass_obj
    def table(switch, json, stale, reachable):
        if json:
            if stale:
                nd.get_neighbor_discovery_table_stale_entries_in_json(switch.switch)
            elif reachable:
                nd.get_neighbor_discovery_table_reachable_entries_in_json(switch.switch)
            else:
                nd.get_neighbor_discovery_table_entries_in_json(switch.switch)   
        else:
            if stale:
                nd.get_neighbor_discovery_table_stale_entries(switch.switch)
            elif reachable:
                nd.get_neighbor_discovery_table_reachable_entries(switch.switch)
            else:
                nd.get_neighbor_discovery_table_entries(switch.switch)   
            
        
class InterfaceCommands(object):
    ''' Interface commands '''

    @click.group(help='Show interface information')
    def interfaces():
        pass


    @click.command(help='Show interfaces in a brief format')
    @click.option('-j', '--json', is_flag=True, help='Output in JSON format')
    @click.option('-i', '--int', default='', help='Show information for a specific interface')
    @click.pass_obj
    def _brief(switch, json, int):
        if int and json:
            interface.get_interfaces_brief_for_specific_interface_in_json(switch.switch, int)
        elif int:
            interface.get_interfaces_brief_for_specific_interface(switch.switch, int)
        elif json:
            interface.get_interfaces_brief_in_json(switch.switch)
        else:
            interface.get_interfaces_brief(switch.switch)


    @click.command(help='Show interfaces descriptions')
    @click.option('-j', '--json', is_flag=True, help='Output in JSON format')
    @click.option('-i', '--int', default='', help='Show descriptions for a specific interface')
    @click.pass_obj
    def _desc(switch, json, int):
        if int and json:
            interface.get_interfaces_descriptions_for_specific_interface_in_json(switch.switch, int)
        elif int:
            interface.get_interfaces_descriptions_for_specific_interface(switch.switch, int)
        elif json:
            interface.get_interfaces_descriptions_in_json(switch.switch)
        else:
            interface.get_interfaces_descriptions(switch.switch)


    @click.command(help='Show interfaces port information')
    @click.option('-j', '--json', is_flag=True, help='Output in JSON format')
    @click.option('-i', '--int', default='', help='Show detailed interface information')
    @click.pass_obj
    def _detail(switch, json, int):
        if int and json:
            interface.get_interfaces_detail_for_specific_interface_in_json(switch.switch, int)
        elif int:
            interface.get_interfaces_detail_for_specific_interface(switch.switch, int)
        elif json:
            interface.get_interfaces_detail_in_json(switch.switch)
        else:
            interface.get_interfaces_detail(switch.switch)
        

    interfaces.add_command(_brief, name='brief')
    interfaces.add_command(_desc, name='desc')
    interfaces.add_command(_detail, name='detail')


class ReloadConfig(object):
    ''' Reload config '''

    @click.command(help='Reload config on a MOSS switch')
    @click.pass_obj
    def reload_config(switch):
        click.confirm('Continuing will interrupt traffic forwarding. Are you sure you want to continue?', 
            abort=True
        )
        
        config.reload(switch.switch)


class RouteCommands(object):
    ''' Route commands '''

    @click.group(help='Show route table information')
    def route():
        pass

    
    @click.command(help='Show BGP routes')
    @click.option('-j', '--json', is_flag=True, help='Output in JSON format')
    @click.option('-p', '--prefix', default='', help='Show routes to specific prefix')
    @click.pass_obj
    def _bgp(switch, json, prefix):
        if prefix:
            if json:
                route.get_bgp_routes_specific_entry_in_json(switch.switch, prefix)
            else:
                route.get_bgp_routes_specific_entry(switch.switch, prefix)
        else:
            if json:
                route.get_bgp_routes_in_json(switch.switch)
            else:
                route.get_bgp_routes(switch.switch)
        

    @click.command(help='Show IPv6 RIB table')
    @click.option('-j', '--json', is_flag=True, help='Output in JSON format')
    @click.option('-p', '--prefix', default='', help='Show routes to specific prefix')
    @click.pass_obj
    def _rib(switch, json, prefix):
        if prefix:
            if json:
                route.get_rib_table_specific_entry_in_json(switch.switch, prefix)
            else:
                route.get_rib_table_specific_entry(switch.switch, prefix)
        else:
            if json:
                route.get_rib_table_in_json(switch.switch)
            else:
                route.get_rib_table(switch.switch)
                
                
    @click.command(help='Show OSPF routes')
    @click.option('-j', '--json', is_flag=True, help='Output in JSON format')
    @click.option('-p', '--prefix', default='', help='Show routes to specific prefix')
    @click.pass_obj
    def _ospf(switch, json, prefix):
        if prefix:
            if json:
                route.get_ospf_routes_specific_entry_in_json(switch.switch, prefix)
            else:
                route.get_ospf_routes_specific_entry(switch.switch, prefix)
        else:
            if json:
                route.get_ospf_routes_in_json(switch.switch)
            else:
                route.get_ospf_routes(switch.switch)
                
    route.add_command(_bgp, name='bgp')
    route.add_command(_ospf, name='ospf')
    route.add_command(_rib, name='rib')


class SystemCommands(object):
    ''' System commands '''

    @click.group(help='Show switch system information')
    def system():
        pass

    @click.command(help='Show switch uptime')
    @click.option('-j', '--json', is_flag=True, help='Output in JSON format')
    @click.pass_obj
    def _uptime(switch, json):
        if json:
            system.get_system_uptime_in_json(switch.switch)
        else:
            system.get_system_uptime(switch.switch)


    @click.command(help='Show switch information')
    @click.option('-j', '--json', is_flag=True, help='Output in JSON format')
    @click.pass_obj
    def _info(switch, json):
        if json:
            system.get_system_info_in_json(switch.switch)
        else:
            system.get_system_info(switch.switch)

        
    system.add_command(_uptime, name='uptime')
    system.add_command(_info, name='info')


class Options(object):
    ''' Hold Show CLI option information '''

    def __init__(self, switch):
        self.switch = switch


# Main body
@click.group()
@click.option('-s', '--switch', default='localhost', help='Name or IPv6 address of switch (default ::1/128)')
@click.pass_context
def main(ctx, switch):
    '''\b
        ______________ _____________  ________ 
        \____    /    |   \______   \/  _____/ 
          /     /|    |   /|       _/   \  ___ 
         /     /_|    |  / |    |   \    \_\  \ \b
        /_______ \______/  |____|_  /\______  /
                \/                \/        \/     
                             
    \033[1;32mzurg\033[0m is a CLI tool for querying \033[1;32mMOSS\033[0m switches
    '''
    ctx.obj = Options(switch)

main.add_command(BgpCommands().bgp)
main.add_command(Ipv6Commands().ipv6)
main.add_command(LldpCommands().lldp)
main.add_command(MacCommands().mac, name='mac-table')
main.add_command(OspfCommands().ospf)
main.add_command(NdCommands().table, name='nd-table')
main.add_command(InterfaceCommands().interfaces)
main.add_command(ReloadConfig().reload_config, name='reload-config')
main.add_command(RouteCommands().route)
main.add_command(ConfCommands().running_config, name="running-config")
main.add_command(SystemCommands().system)


if __name__ == "__main__":
    main()
