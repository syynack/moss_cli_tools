#!/usr/bin/python

import click
import sys

from ops import log
from ops.build import BuildUtils
from ops.build import DefinitionUtils


class BuildCommands():
    
    @click.command(help='Build configuration files a clos fabric')
    @click.pass_obj
    def clos(options):
        BuildUtils().build_clos(options.template_dir)
    
    
    @click.command(help='Build configuration files for the spine')
    @click.option('-f', '--full', is_flag=True, help='Build the entire spine')
    @click.option('-r', '--row-number', default=0, help='Build config for a specific spine row')
    @click.pass_obj
    def spine(options, full, row_number):
        if full and not row_number:
            BuildUtils().build_spine(options.template_dir)
        elif row_number and not full:
            BuildUtils().build_spine_row(row_number, options.template_dir)
        else:
            print 'No valid options passed\n\t--full: Build the entire spine\n\t--row-number: Build specific row\n'
    
    
    @click.command(help='Build configuration files for a pod')
    @click.option('-f', '--full', is_flag=True, help='Build all pods')
    @click.option('-p', '--pod-number', default=0, help='Target pod number')
    @click.pass_obj
    def pod(options, full, pod_number):
        if full and not pod_number:
            BuildUtils().build_pod(options.template_dir)
        elif pod_number and not full:
            BuildUtils().build_specific_pod(pod_number, options.template_dir)
        else:
            print 'No valid options passed\n\t--full: Build the entire pod\n\t--pod-number: Build specific pod\n'
        
    
    @click.command(help='Build leaf 1 configuration files for a pod')
    @click.option('-f', '--full', is_flag=True, help='Build all pods')
    @click.option('-p', '--pod-number', default=0, help='Target pod number')
    @click.pass_obj
    def leaf1(options, full, pod_number):
        if full and not pod_number:
            BuildUtils().build_pod_leaf_1(options.template_dir)
        elif pod_number and not full:
            BuildUtils().build_pod_leaf_1_specific_pod(pod_number, options.template_dir)
        else:
            print 'No valid options passed\n\t--full: Build the entire pod l1\n\t--pod-number: Build specific pod l1\n'
            
            
    @click.command(help='Build leaf 2 configuration files for a pod')
    @click.option('-f', '--full', is_flag=True, help='Build all pods')
    @click.option('-p', '--pod-number', default=0, help='Target pod number')
    @click.pass_obj
    def leaf2(options, full, pod_number):
        if full and not pod_number:
            BuildUtils().build_pod_leaf_2(options.template_dir)
        elif pod_number and not full:
            BuildUtils().build_pod_leaf_2_specific_pod(pod_number, options.template_dir)
        else:
            print 'No valid options passed\n\t--full: Build the entire pod l2\n\t--pod-number: Build specific pod l2\n'
    
    
    @click.command(help='Build configuration files for a switch')
    @click.option('-H', '--hostname', default='', help='Hostname of the target switch')
    @click.pass_obj
    def switch(options, hostname):
        if not hostname:
            print 'A hostname is required with -H, --hostname'
            sys.exit()
            
        BuildUtils().build_switch(hostname, options.template_dir)
        
    
class BuildOptions():
    
    def __init__(self, template_dir):
        self.template_dir = template_dir


class DeployCommands():
    pass


@click.group(short_help='Build configuration files')
@click.option('-d', '--template-dir', default='', help='Directory location of JSON templates')
@click.pass_context
def build(ctx, template_dir):
    '''
    \b
    \033[1;32mbuild()\033[0m is used for building Quagga and Linux network
    configuration files for switches running MOSS. 
    
    \b
    These configuration files must first be defined
    using \033[1;32mdefine()\033[0m, this will create JSON configuration 
    templates which \033[1;32mbuild()\033[0m will then use to build 
    consistent device configuration for a clos fabric.
    '''
    
    ctx.obj = BuildOptions(template_dir)
    
    log.verbose('build')
    
build.add_command(BuildCommands().clos)
build.add_command(BuildCommands().spine)
build.add_command(BuildCommands().pod)
build.add_command(BuildCommands().leaf1, name='leaf-1')
build.add_command(BuildCommands().leaf2, name='leaf-2')
build.add_command(BuildCommands().switch)


@click.command(short_help='Define device config through templates')
@click.option('-dcn', '--data-center-number', default=1, help='Datacenter number')
@click.option('-gr', '--global-routing', default='fd35::/16', help='/16 IPv6 routing prefix for global routing')
@click.option('-if', '--interface-format', default='et', help='Interface names to be used (default: et)')
@click.option('-sr', '--spine-rows', default=4, help='Total number of spine rows')
@click.option('-tr', '--tor-routing', default='2001::/16', help='/16 IPv6 routing prefix for TOR subnets')
@click.option('-tc', '--tor-count', default=256, help='Number of TORs (default: 256)')
def define(data_center_number, global_routing, interface_format, spine_rows, tor_routing, tor_count):
    '''
    \b
    \033[1;32mdefine()\033[0m is used for defining network device configuration
    in the form of JSON files. Which can then be built into
    Quagga and Linux configuration files using \033[1;32mbuild()\033[0m.
    '''
    
    log.verbose('Starting define()')
    click.confirm('Proceed to define configuration templates for the entire clos?', abort=True)
    
    if tor_count > 512:
        click.confirm('Specifying {} will create {} pods. Do you want to continue?'.format(tor_count, tor_count / 64), abort=True)
        
    log.verbose('Proceeding to create definition templates')
    dc_var_result = DefinitionUtils().define_data_center_vars(data_center_number, global_routing, interface_format, spine_rows, tor_routing, tor_count)
    log.verbose('Finished creating variables for data center configuration templates')
    
    if dc_var_result["status"] != 'ok':
        log.error('moss failed to define datacenter variables')
        sys.exit()
        
    log.verbose('Defining data center variables returned status {}'.format(dc_var_result["status"]))
    
    dc_vars = dc_var_result["dc_vars"]
    log.verbose('Proceeding to create the file structure for clos network')
    fs_creation_result = DefinitionUtils().create_data_center_file_structure(dc_vars)
    log.verbose('Finished creating file structure for clos network')
    
    if fs_creation_result["status"] != 'ok':
        log.error('moss failed to create the data center file structure')
        sys.exit()
        
    log.verbose('Creating data center file structure return status {}'.format(fs_creation_result["status"]))
        
    log.verbose('Proceeding to create clos configuration definitions')
    config_definition_result = DefinitionUtils().create_data_center_config_definitions(dc_vars)
    log.verbose('Finished creating configuration definition files for clos network')
    
    if config_definition_result["status"] != 'ok':
        log.error('dmoss failed to create device configuration definitions')
        sys.exit()
        
    log.verbose('Creating data center config definitions returned status {}'.format(config_definition_result["status"]))
    log.verbose('Created {} files'.format(config_definition_result["total_files"]))
    log.verbose('Consumed {}KB of disk space'.format(config_definition_result["space_consumed"] / 1024))
    log.info('moss def-config completed')
        

@click.group(short_help='Deploy configuration files to devices')
def deploy():
    '''
    \b
    \033[1;32mdeploy()\033[0m is used for deploying configuration files
    built using \033[1;32mdefine()\033[0m and \033[1;32mbuild()\033[0m to one, a selection, 
    or many MOSS switches safely and securely.
    '''
    pass


@click.group()
@click.option('-v', '--verbose', is_flag=True, help='Enable verbose logging')
@click.pass_context
def main(ctx, verbose):
    '''\b
            ___  ________ _____ _____ 
            |  \/  |  _  /  ___/  ___|
            | .  . | | | \ `--.\ `--. 
            | |\/| | | | |`--. \`--. \ \b
            | |  | \ \_/ /\__/ /\__/ /
            \_|  |_/\___/\____/\____/                  
                          
    \033[1;32mmoss\033[0m is a CLI tool for managing \033[1;32mMOSS\033[0m switches
    '''
    
    if verbose:
        log.set_verbose()
        
    
main.add_command(build, name='build-config')
main.add_command(define, name='def-config')
main.add_command(deploy, name='deploy-config')
    
    
if __name__ == "__main__":
    main()