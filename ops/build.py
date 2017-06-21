#!/usr/bin/python

import click
import os
import yaml
import jinja2
import sys
import time

from ops import log
from ops.connection import Session

LOOPBACK_FORMAT = '{}:{}:{}:{}::{}'
LOOPBACK_FORMAT_WITH_MASK = '{}:{}:{}:{}::{}/128'
TOR_FACING_DESCRIPTION = "TOR facing port"
CORE_FACING_DESCRIPTION = "Core facing port"
SPINE_DESCRIPTION = "{} {}{} <> {}-s{}-r{} {}{}"
POD_L1_DESCRIPTION = "{} {}{} <> {}-p{}-l1-r{} {}{}"
POD_L2_DESCRIPTION = "{} {}{} <> {}-p{}-l2-r{} {}{}"


class BuildUtils():
    
    def _write_rendered_data_to_file(self, dir, file, template_file, output_file):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        config_dir = '/'.join(current_dir.split('/')[:-1])
        
        env = jinja2.Environment(
            loader = jinja2.FileSystemLoader(config_dir + '/conf/'),
            trim_blocks = True,
            lstrip_blocks = True
        )
        
        template = env.get_template(template_file)
        with open(dir + '/' + file, 'r') as yaml_file:
            yaml_data = yaml.load(yaml_file)
        
            with open(dir + '/' + output_file, 'w+') as config_file:
                config_file_result = template.render(yaml_data)
                config_file.write(config_file_result)
                
    
    def _render_from_template(self, dir, file):
        self._write_rendered_data_to_file(dir, file, 'quagga.jinja', 'Quagga.conf')
        self._write_rendered_data_to_file(dir, file, 'network.jinja', 'interfaces')
    
    
    def build_clos(self, template_dir):
        for subdir, dir, files in os.walk(template_dir):
            for file in files:
                if file != 'def_dc.yaml':
                    self._render_from_template(subdir, file)
    
    
    def build_spine(self, template_dir):
        for subdir, dir, files in os.walk(template_dir):
            for file in files:
                if '-s' in file:
                    self._render_from_template(subdir, file)
    
    
    def build_spine_row(self, row_number, template_dir):
        for subdir, dir, files in os.walk(template_dir):
            for file in files:
                if '-s' + str(row_number) in file:
                    self._render_from_template(subdir, file)
    
    
    def build_pod(self, template_dir):
        for subdir, dir, files in os.walk(template_dir):
            for file in files:
                if '-p' in file:
                    self._render_from_template(subdir, file)
    
    
    def build_specific_pod(self, pod_number, template_dir):
        for subdir, dir, files in os.walk(template_dir):
            for file in files:
                if '-p' + str(pod_number) in file:
                    self._render_from_template(subdir, file)
    
    
    def build_pod_leaf_1(self, template_dir):
        for subdir, dir, files in os.walk(template_dir):
            for file in files:
                if '-l1' in file:
                    self._render_from_template(subdir, file)
    
    
    def build_pod_leaf_1_specific_pod(self, pod_number, template_dir):
        for subdir, dir, files in os.walk(template_dir):
            for file in files:
                if '-p' + str(pod_number) in file and '-l1' in file:
                    self._render_from_template(subdir, file)
    
    
    def build_pod_leaf_2(self, template_dir):
        for subdir, dir, files in os.walk(template_dir):
            for file in files:
                if '-l2' in file:
                    self._render_from_template(subdir, file)
    
    
    def build_pod_leaf_2_specific_pod(self, pod_number, template_dir):
        for subdir, dir, files in os.walk(template_dir):
            for file in files:
                if '-p' + str(pod_number) in file and '-l2' in file:
                    self._render_from_template(subdir, file)
    
    
    def build_switch(self, hostname, template_dir):
        for subdir, dir, files in os.walk(template_dir):
            for file in files:
                if hostname in file:
                    self._render_from_template(subdir, file)


class DefinitionUtils():
    
    def define_data_center_vars(self, data_center_number, global_routing, interface_format, spine_rows, tor_routing, tor_count):
        '''
        Summary:
        Builds dictionary for use throughout building datacenter configs.
        
        Takes:
        data_center_number: int
        global_routing: string
        interface_format: string
        spine_rows: int
        tor_routing: string
        tor_count: int
        
        Returns:
        dict
        '''
        
        log.verbose('Starting definition of data center variables')
        log.verbose('Data center number: {}'.format(data_center_number))
        log.verbose('Global routing prefix: {}'.format(global_routing))
        log.verbose('TOR routing prefix: {}'.format(tor_routing))
        log.verbose('Global interface format: {}'.format(interface_format))
        log.verbose('Spine rows: {}'.format(spine_rows))
        log.verbose('Total TOR count: {}'.format(tor_count))
        
        switches_per_pod = 32
        tor_ups = 4
        spine_ups = 4
        core_ups = 4
        tor_facing_ports_per_pod = (switches_per_pod / 2) * (switches_per_pod / 2)
        total_pods = tor_count / (tor_facing_ports_per_pod / tor_ups)
        total_tor_facing_ports = tor_facing_ports_per_pod * total_pods
        total_switches = switches_per_pod * total_pods
        pod_internal = tor_facing_ports_per_pod
        total_pod_internal = pod_internal * total_pods
        dc_prefix = 'd{}'.format(data_center_number)
        
        log.verbose('Finished calculating total variables')
        log.verbose('Proceeding with calculations for def_dc.json')
        
        dc_vars = {
            "dcn": data_center_number,
            "dc_prefix": dc_prefix,
            "interface_format": interface_format,
            "routing": {
                "global_p2p": global_routing,
                "tor_routed": tor_routing
            },
            "spines_in_service": [i for i in range(1, spine_rows + 1)],
            "switchport_density": {
                "spine": 32,
                "pod": 32,
                "tor": 32
            },
            "total_tors": tor_count,
            "total_switches": total_switches,
            "total_switches_per_pod": switches_per_pod,
            "total_spine_switches": (switches_per_pod / 2) * spine_rows,
            "total_switches_per_spine": switches_per_pod / 2,
            "total_spine_rows": spine_rows,
            "total_interfaces": (total_switches * switches_per_pod) + \
                                (((switches_per_pod / 2) * spine_rows) * switches_per_pod) + \
                                (tor_count * tor_ups),
            "total_links": ((total_switches * switches_per_pod) + \
                           (((switches_per_pod / 2) * spine_rows) * switches_per_pod) + \
                           (tor_count * tor_ups)) / 2,
            "total_pods": total_pods,
            "pods_in_service": [i for i in range(1, total_pods + 1)],
            "uplinks": {
                "tor_to_l1": tor_ups * tor_count,
                "l1_to_l2": total_pod_internal,
                "l2_to_spine": ((switches_per_pod / 2) * spine_ups) * total_pods,
                "spine_to_core": ((switches_per_pod / 2) * spine_rows) * core_ups
            },
            "gen_status": 'ok'
        }
        
        log.verbose('Finished calculations for def_dc.json')
        
        return {
            "status": "ok" if dc_vars.get('gen_status') else 'fail',
            "dc_vars": dc_vars
        }
    
    
    def _define_bgp_peers(self, switch, local_loopback, type):
        '''
        Summary:
        Builds a list or dictionary of BGP peer loopback addresses depending on the layer
        
        Takes:
        switch: string, bgp_router_id
        local_loopback: string
        tyoe: int
        
        Returns:
        dict or list
        '''
        
        local_loopback = local_loopback.split(':')
        global_routing = local_loopback[0]
        datacenter_number = local_loopback[1]
        pod = local_loopback[2]
        
        bgp_peers = []
        
        for peer in range(1, 17):
            if type == 1:
                bgp_peers.append(LOOPBACK_FORMAT.format(global_routing, datacenter_number, pod, 2, peer))
            elif type == 2:
                bgp_peers.append(LOOPBACK_FORMAT.format(global_routing, datacenter_number, pod, 1, peer))
                bgp_peers.append(LOOPBACK_FORMAT.format(global_routing, datacenter_number, peer, 53, switch))
            elif type == 53:
                bgp_peers.append(LOOPBACK_FORMAT.format(global_routing, datacenter_number, pod, 2, peer))
        
        return bgp_peers
    
    
    def _define_portmap(self, dc_prefix, hostname, interface_format, pod, type, switch):
        '''
        Summary:
        Build a dictionary for the port mappings of a given device layer
        
        Takes:
        dc_prefix: string
        hostname: string, from switch_vars["hostname"]
        interface_format: string, from switch_vars["interface_format"]
        pod: int
        type: int, [1, 2, 53] (l1, l2, spine)
        switch: int
        
        Returns:
        dict
        '''
          
        portmap = {}
            
        for port_number in range(1, 33):
            port_id = "{}{}".format(interface_format, port_number)
            portmap[port_id] = {}
            portmap[port_id]["index"] = port_number
                           
            if type == 1:
                if port_number > 16:
                    portmap[port_id]["description"] = TOR_FACING_DESCRIPTION
                else:
                    portmap[port_id]["description"] = POD_L2_DESCRIPTION \
                        .format(hostname, interface_format, port_number, dc_prefix, pod, port_number, interface_format, switch)  
                        
            elif type == 2:
                if port_number < 17:
                    portmap[port_id]["description"] = POD_L1_DESCRIPTION \
                        .format(hostname, interface_format, port_number, dc_prefix, pod, port_number, interface_format, switch)
                else:
                    portmap[port_id]["description"] = SPINE_DESCRIPTION \
                        .format(hostname, interface_format, port_number, dc_prefix, port_number - 16, switch, interface_format, pod)
                    
            elif type == 53:
                if port_number < 17:
                    portmap[port_id]["description"] = POD_L2_DESCRIPTION \
                        .format(hostname, interface_format, port_number, dc_prefix, port_number, switch, interface_format, switch + 16)  
                else:
                    portmap[port_id]["description"] = CORE_FACING_DESCRIPTION
        
        return portmap
    
    
    def create_data_center_file_structure(self, dc_vars):
        '''
        Summary:
        Creates physical local directories and JSON config template files for devices
        
        Takes:
        dc_vars: dict
        
        Returns:
        dict
        '''
        
        log.verbose('Starting the creation of the clos file structure')
        
        dc_prefix = dc_vars["dc_prefix"]
        
        log.verbose('Checking if directories already exist')
        
        if not os.path.exists(dc_prefix):
            log.verbose("Directories don't exist, so making them")
            os.makedirs(dc_prefix)
            
        log.verbose('Directories already exist')
        log.verbose('Starting to build spine files')
        
        for spine in dc_vars["spines_in_service"]:
            spine_prefix = dc_prefix + '-s' + str(spine)
            if not os.path.exists(dc_prefix + '/' + spine_prefix):
                os.makedirs(dc_prefix + '/' + spine_prefix)
                
                for i in range(1, dc_vars["total_switches_per_spine"] + 1):
                    spine_dir = '{}/{}/{}-r{}'.format(dc_prefix, spine_prefix, spine_prefix, i)
                    os.makedirs(spine_dir)
                    with open('{}/{}-r{}.yaml'.format(spine_dir, spine_prefix, i), 'w+') as create_file:
                        create_file.close()
                    
        log.verbose('Finished building spine files')
        log.verbose('Starting to build pod files')
                
        for pod in dc_vars["pods_in_service"]:
            pod_prefix = dc_prefix + '-p' + str(pod)
            if not os.path.exists(dc_prefix + '/' + pod_prefix):
                os.makedirs(dc_prefix + '/' + pod_prefix)
                
                for i in range(1, (dc_vars["total_switches_per_pod"] / 2) + 1):
                    leaf_dir = '{}/{}/{}-l2-r{}'.format(dc_prefix, pod_prefix, pod_prefix, i)
                    os.makedirs(leaf_dir)
                    with open('{}/{}-l2-r{}.yaml'.format(leaf_dir, pod_prefix, i), 'w+') as create_file:
                        create_file.close()
                    
                for i in range(1, (dc_vars["total_switches_per_pod"] / 2) + 1):
                    leaf_dir = '{}/{}/{}-l1-r{}'.format(dc_prefix, pod_prefix, pod_prefix, i)
                    os.makedirs(leaf_dir)
                    with open('{}/{}-l1-r{}.yaml'.format(leaf_dir, pod_prefix, i), 'w+') as create_file:
                        create_file.close()
                    
        log.verbose('Finished building pod files')
        log.verbose('Proceeding to write to def_dc.yaml')     
            
        with open(dc_vars["dc_prefix"] + '/def_dc.yaml', 'w+') as def_dc:
            yaml.dump(dc_vars, def_dc, indent=4, default_flow_style=False)
            
        log.verbose('YAML written to def_dc.yaml')
                    
        return {
            "status": "ok"
        }
    
    
    def create_data_center_config_definitions(self, dc_vars):
        '''
        Summary:
        Creates JSON config templates for all devices defined in create_data_center_file_structure
        
        Takes:
        dc_vars: dict
        
        Returns:
        dict
        '''
        
        SWITCH_COUNT = 0
        log.verbose('Starting to populate individual switch files')
        
        dc_prefix = dc_vars["dc_prefix"]
        data_center_number = dc_vars["dcn"]
        
        log.verbose('Defining switch variables')
        log.verbose('Populating configuration templates for pod switches')    
        
        for pod in dc_vars["pods_in_service"]:
            for leaf in range(1, 3):
                for switch in range(1, 17):
                    temp_switch_vars = {}
                    temp_switch_vars["router_id"] = "{}.{}.{}.{}".format(data_center_number, pod, leaf, switch)
                    temp_switch_vars["hostname"] = "{}-p{}-l{}-r{}".format(dc_prefix, pod, leaf, switch)
                    temp_switch_vars["loopback_ip"] = LOOPBACK_FORMAT_WITH_MASK \
                        .format(dc_vars["routing"]["global_p2p"].split('::')[0], data_center_number, pod, leaf, switch)
                    temp_switch_vars["ospf_area_interface_mappings"] = {"0.0.0.{}".format(pod): [], "0.0.0.0": []}
                    
                    portmap = self._define_portmap(dc_prefix, temp_switch_vars["hostname"], dc_vars["interface_format"], pod, leaf, switch)
                    temp_switch_vars["interfaces"] = portmap
                    
                    bgp_peers = self._define_bgp_peers(temp_switch_vars["router_id"].split('.')[3], temp_switch_vars["loopback_ip"], leaf)
                    temp_switch_vars["bgp_peers"] = bgp_peers
                    
                    for interface in temp_switch_vars["interfaces"]:
                        if temp_switch_vars["interfaces"][interface].get("index") < 17:
                            temp_switch_vars["ospf_area_interface_mappings"]["0.0.0.{}".format(pod)].append(interface)
                        else:
                            if leaf == 2:
                                temp_switch_vars["ospf_area_interface_mappings"]["0.0.0.0"].append(interface)
                                    
                    with open('{}/{}-p{}/{}-p{}-l{}-r{}/{}-p{}-l{}-r{}.yaml'.format(dc_prefix, dc_prefix, pod, dc_prefix, pod, leaf, switch, dc_prefix, pod, leaf, switch), 'w+') as switch_file:                            
                        yaml.dump(temp_switch_vars, switch_file, indent=4, default_flow_style=False)
                        
                    SWITCH_COUNT += 1
                        
        log.verbose('Finished populating pod switch configuration templates')
        log.verbose('Populating configuration templates for spine switches')
                            
        for spine in dc_vars["spines_in_service"]:
            for switch in range(1, 17):
                temp_switch_vars = {}
                temp_switch_vars["router_id"] = "{}.{}.{}.{}".format(data_center_number, spine, 53, switch)
                temp_switch_vars["hostname"] = "{}-s{}-r{}".format(dc_prefix, spine, switch)
                temp_switch_vars["loopback_ip"] = LOOPBACK_FORMAT_WITH_MASK \
                    .format(dc_vars["routing"]["global_p2p"].split('::')[0], data_center_number, spine, 53, switch)
                temp_switch_vars["ospf_area_interface_mappings"] = {"0.0.0.0": []}
                
                portmap = self._define_portmap(dc_prefix, temp_switch_vars["hostname"], dc_vars["interface_format"], spine, 53, switch)
                temp_switch_vars["interfaces"] = portmap
                
                bgp_peers = self._define_bgp_peers(temp_switch_vars["router_id"].split('.')[3], temp_switch_vars["loopback_ip"], 53)
                temp_switch_vars["bgp_peers"] = bgp_peers
                
                for interface in temp_switch_vars["interfaces"]:
                    if temp_switch_vars["interfaces"][interface]["index"] < 17:
                        temp_switch_vars["ospf_area_interface_mappings"]["0.0.0.0"].append(interface)
                
                with open('{}/{}-s{}/{}-s{}-r{}/{}-s{}-r{}.yaml'.format(dc_prefix, dc_prefix, spine, dc_prefix, spine, switch, dc_prefix, spine, switch), 'w+') as switch_file:                            
                    yaml.dump(temp_switch_vars, switch_file, indent=4, default_flow_style=False)
                    
                SWITCH_COUNT += 1
                    
        log.verbose('Finished populating spine switch configuration templates')
        
        total_size = 0
        size_format = 'KB'
        
        for dirpath, dirnames, filenames in os.walk(dc_prefix):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
                
        if total_size > 1024:
            size_format = 'MB'
                    
        return {
            "status": "ok",
            "total_files": SWITCH_COUNT,
            "space_consumed": "{}{}".format(str(total_size), size_format)
        }
    
    
class DeploymentUtils():
    
    def deploy_config(self, file, target, port):
        log.info('Preparing to send new configuration to {}:{}'.format(target, port))
        log.verbose('Removing old configuration from {}'.format(target))
        
        session = Session().ssh(target)
        command = 'rm /etc/quagga/Quagga.conf'
        result = session.send_command(command)
        
        if 'Cannot' in result:
            log.error('Unable to remove Quagga configuration at {}:/etc/quagga/Quagga.conf'.format(hostname))
            sys.exit()
            
        log.verbose('Successfully removed old configuration from {}'.format(target))
        log.verbose('Preparing to SCP new Quagga.conf')
        
        scp_result = Session().scp_quagga_configuration_file(file, target, port)
        
        if scp_result["status"] == 'fail':
            log.error('Could not SCP file due to: {}'.format(scp_result["reason"]))
            sys.exit()
            
        log.info('Successfully copied Quagga.conf to {}'.format(target))
        click.confirm('Proceed to restart Quagga on {}?'.format(target), abort=True)
        
        result = session.send_command('/etc/init.d/quagga force-reload')
        
        log.info('Sleeping for 5 seconds for Quagga to restart')
        time.sleep(5)
        
        result = session.send_command('ps -ef | grep quagga')
        result = result.splitlines()
        
        if len(result) < 2:
            log.error('Restart of Quagga on {} was unsuccessful!'.format(target))
            
        log.info('Quagga on {} was successfully reloaded'.format(target))  