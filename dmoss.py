#!/usr/bin/python

import click
import sys

from ops import log
from ops.build import DefinitionUtils

@click.command()
@click.option('-dcn', '--data-center-number', default=1, help='Datacenter number')
@click.option('-gr', '--global-routing', default='fd35::/16', help='/16 IPv6 routing prefix for global routing')
@click.option('-if', '--interface-format', default='et', help='Interface names to be used (default: et)')
@click.option('-sr', '--spine-rows', default=4, help='Total number of spine rows')
@click.option('-tr', '--tor-routing', default='2001::/16', help='/16 IPv6 routing prefix for TOR subnets')
@click.option('-tc', '--tor-count', default=256, help='Number of TORs (default: 256)')
def main(data_center_number, global_routing, interface_format, spine_rows, tor_routing, tor_count):
    '''
    \b
    \033[1;32mdmoss\033[0m is a CLI tool for generating \033[1;32mMOSS\033[0m configuration templates
    '''
    log.debug('Starting dmoss')
    
    dc_var_result = DefinitionUtils().define_data_center_vars(data_center_number, global_routing, interface_format, spine_rows, tor_routing, tor_count)
    
    if dc_var_result["status"] != 'ok':
        log.error('dmoss failed to define datacenter variables')
        sys.exit()
        
    log.debug('dmoss successfully defined datacenter variables')
    
    dc_vars = dc_var_result["dc_vars"]
    fs_creation_result = DefinitionUtils().create_data_center_file_structure(dc_vars)
    
    if fs_creation_result["status"] != 'ok':
        log.error('dmoss failed to create the data center file structure')
        sys.exit()
        
    log.debug('dmoss successfully created the data center file structure')
    
    config_definition_result = DefinitionUtils().create_data_center_config_definitions(dc_vars)
    
    if config_definition_result["status"] != 'ok':
        log.error('dmoss failed to create device configuration definitions')
        sys.exit()
        
    log.debug('dmoss successfully created device configuration definitions')
        
        
if __name__ == '__main__':
    main()