#!/usr/bin/python

import os
import json
import jinja2

from ops import log

LOOPBACK_FORMAT = '{}:{}:{}:{}::{}' # Global routing prefix, datacenter number, spine/pod number, layer, router number
LOOPBACK_FORMAT_WITH_MASK = '{}:{}:{}:{}::{}/128'
TOR_FACING_DESCRIPTION = "TOR facing port"
CORE_FACING_DESCRIPTION = "Core facing port"
SPINE_DESCRIPTION = "{} {}{} <> {}-s{}-r{} {}{}"
POD_L1_DESCRIPTION = "{} {}{} <> {}-p{}-l1-r{} {}{}"
POD_L2_DESCRIPTION = "{} {}{} <> {}-p{}-l2-r{} {}{}"


class BuildUtils():
    
    def _render_from_template(self, dir, file):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        config_dir = '/'.join(current_dir.split('/')[:-1])
        
        env = jinja2.Environment(
            loader = jinja2.FileSystemLoader(config_dir + '/conf/'),
            trim_blocks = True,
            lstrip_blocks = True
        )
                            
        template = env.get_template('quagga.jinja')
        with open(dir + '/' + file, 'r') as json_file:
            json_data = json.load(json_file)
        
            with open(dir + '/Quagga.conf', 'w+') as config_file:
                config_file_result = template.render(json_data)
                config_file.write(config_file_result)
    
    
    def build_clos(self, template_dir):
        for subdir, dir, files in os.walk(template_dir):
            for file in files:
                if file != 'def_dc.json':
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
        
        log.verbose('Finished calculating total variables')
        log.verbose('Proceeding with calculations for def_dc.json')
        
        dc_vars = {}
        dc_vars["dcn"] = data_center_number
        dc_vars["dc_prefix"] = 'd{}'.format(dc_vars["dcn"])
        dc_vars["interface_format"] = interface_format
        dc_vars["routing"] = {}
        dc_vars["routing"]["global_p2p"] = global_routing
        dc_vars["routing"]["tor_routed"] = tor_routing
        dc_vars["spines_in_service"] = []
        
        for i in range(1, spine_rows + 1):
            dc_vars["spines_in_service"].append(i)
            
        dc_vars["switchport_density"] = {}
        dc_vars["switchport_density"]["spine"] = 32
        dc_vars["switchport_density"]["pod"] = 32
        dc_vars["switchport_density"]["tor"] = 32
        dc_vars["total_tors"] = tor_count
        dc_vars["total_switches"] = total_switches
        dc_vars["total_switches_per_pod"] = switches_per_pod
        dc_vars["total_spine_switches"] = (switches_per_pod / 2) * spine_rows
        dc_vars["total_switches_per_spine"] = switches_per_pod / 2
        dc_vars["total_spine_rows"] = len(dc_vars["spines_in_service"])
        dc_vars["total_interfaces"] = (total_switches * switches_per_pod) + \
                                      (dc_vars["total_spine_switches"] * switches_per_pod) + \
                                      (tor_count * tor_ups)
        dc_vars["total_links"] = dc_vars["total_interfaces"] / 2
        dc_vars["total_pods"] = total_pods
        dc_vars["pods_in_service"] = []
        
        for i in range(1, total_pods + 1):
            dc_vars["pods_in_service"].append(i)
            
        dc_vars["uplinks"] = {}
        dc_vars["uplinks"]["serv_to_l1"] = tor_ups * tor_count
        dc_vars["uplinks"]["l1_to_l2"] = total_pod_internal
        dc_vars["uplinks"]["l2_to_spine"] = ((switches_per_pod / 2) * spine_ups) * total_pods
        dc_vars["uplinks"]["spine_to_core"] = ((switches_per_pod / 2) * len(dc_vars["spines_in_service"])) * core_ups
        dc_vars["gen_status"] = 'ok'
        
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
        
        interfaces_list = []
               
        for port_number in range(1, 33):
            portmap = {}
            portmap["port_id"] = "{}{}".format(interface_format, port_number)
                           
            if type == 1:
                if port_number > 16:
                    portmap["description"] = TOR_FACING_DESCRIPTION
                else:
                    portmap["description"] = POD_L2_DESCRIPTION \
                        .format(hostname, interface_format, port_number, dc_prefix, pod, port_number, interface_format, switch)  
                        
            elif type == 2:
                if port_number < 17:
                    portmap["description"] = POD_L1_DESCRIPTION \
                        .format(hostname, interface_format, port_number, dc_prefix, pod, port_number, interface_format, switch)
                else:
                    portmap["description"] = SPINE_DESCRIPTION \
                        .format(hostname, interface_format, port_number, dc_prefix, port_number - 16, switch, interface_format, pod)
                    
            elif type == 53:
                if port_number < 17:
                    portmap["description"] = POD_L2_DESCRIPTION \
                        .format(hostname, interface_format, port_number, dc_prefix, port_number, switch, interface_format, switch + 16)  
                else:
                    portmap["description"] = CORE_FACING_DESCRIPTION
                    
            interfaces_list.append(portmap)
        
        return interfaces_list
    
    
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
                    with open('{}/{}-r{}.json'.format(spine_dir, spine_prefix, i), 'w+') as create_file:
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
                    with open('{}/{}-l2-r{}.json'.format(leaf_dir, pod_prefix, i), 'w+') as create_file:
                        create_file.close()
                    
                for i in range(1, (dc_vars["total_switches_per_pod"] / 2) + 1):
                    leaf_dir = '{}/{}/{}-l1-r{}'.format(dc_prefix, pod_prefix, pod_prefix, i)
                    os.makedirs(leaf_dir)
                    with open('{}/{}-l1-r{}.json'.format(leaf_dir, pod_prefix, i), 'w+') as create_file:
                        create_file.close()
                    
        log.verbose('Finished building pod files')
        log.verbose('Proceeding to write to def_dc.json')     
            
        with open(dc_vars["dc_prefix"] + '/def_dc.json', 'w+') as def_dc:
            def_dc.write(json.dumps(dc_vars, sort_keys=True, indent=4))
            
        log.verbose('JSON written to def_dc.json')
                    
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
        
        switch_vars = {
            "bgp_peer_options": [],
            "bgp_peer_ipv6_unicast_options": ['soft-reconfiguration inbound'],
            "options": ['service integrated-vtysh-config', 'log syslog', 'log commands']
        }
          
        log.verbose('Populating configuration templates for pod switches')    
        
        for pod in dc_vars["pods_in_service"]:
            for leaf in range(1, 3):
                for switch in range(1, 17):
                    temp_switch_vars = switch_vars
                    temp_switch_vars["bgp_router_id"] = "{}.{}.{}.{}".format(data_center_number, pod, leaf, switch)
                    temp_switch_vars["hostname"] = "{}-p{}-l{}-r{}".format(dc_prefix, pod, leaf, switch)
                    temp_switch_vars["loopback_ip"] = LOOPBACK_FORMAT_WITH_MASK \
                        .format(dc_vars["routing"]["global_p2p"].split('::')[0], data_center_number, pod, leaf, switch)
                    temp_switch_vars["ospf_router_id"] = "{}.{}.{}.{}".format(data_center_number, pod, leaf, switch)
                    temp_switch_vars["ospf_area"] = "0.0.0.{}".format(pod)
                    
                    portmap = self._define_portmap(dc_prefix, temp_switch_vars["hostname"], dc_vars["interface_format"], pod, leaf, switch)
                    temp_switch_vars["interfaces"] = portmap
                    
                    bgp_peers = self._define_bgp_peers(temp_switch_vars["bgp_router_id"].split('.')[3], temp_switch_vars["loopback_ip"], leaf)
                    temp_switch_vars["bgp_peers"] = bgp_peers
                                    
                    with open('{}/{}-p{}/{}-p{}-l{}-r{}/{}-p{}-l{}-r{}.json'.format(dc_prefix, dc_prefix, pod, dc_prefix, pod, leaf, switch, dc_prefix, pod, leaf, switch), 'w+') as switch_file:                            
                        switch_file.write(json.dumps(temp_switch_vars, sort_keys=True, indent=4))
                        
                    SWITCH_COUNT += 1
                        
        log.verbose('Finished populating pod switch configuration templates')
        log.verbose('Populating configuration templates for spine switches')
                            
        for spine in dc_vars["spines_in_service"]:
            for switch in range(1, 17):
                temp_switch_vars = switch_vars
                temp_switch_vars["bgp_router_id"] = "{}.{}.{}.{}".format(data_center_number, spine, 53, switch)
                temp_switch_vars["hostname"] = "{}-s{}-r{}".format(dc_prefix, spine, switch)
                temp_switch_vars["loopback_ip"] = LOOPBACK_FORMAT_WITH_MASK \
                    .format(dc_vars["routing"]["global_p2p"].split('::')[0], data_center_number, spine, 53, switch)
                temp_switch_vars["ospf_router_id"] = "{}.{}.{}.{}".format(data_center_number, spine, 53, switch)
                temp_switch_vars["ospf_area"] = "0.0.0.0"
                
                portmap = self._define_portmap(dc_prefix, temp_switch_vars["hostname"], dc_vars["interface_format"], spine, 53, switch)
                temp_switch_vars["interfaces"] = portmap
                
                bgp_peers = self._define_bgp_peers(temp_switch_vars["bgp_router_id"].split('.')[3], temp_switch_vars["loopback_ip"], 53)
                temp_switch_vars["bgp_peers"] = bgp_peers
                
                with open('{}/{}-s{}/{}-s{}-r{}/{}-s{}-r{}.json'.format(dc_prefix, dc_prefix, spine, dc_prefix, spine, switch, dc_prefix, spine, switch), 'w+') as switch_file:                            
                    switch_file.write(json.dumps(temp_switch_vars, sort_keys=True, indent=4))
                    
                SWITCH_COUNT += 1
                    
        log.verbose('Finished populating spine switch configuration templates')
        
        total_size = 0
        
        for dirpath, dirnames, filenames in os.walk(dc_prefix):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
                    
        return {
            "status": "ok",
            "total_files": SWITCH_COUNT,
            "space_consumed": total_size
        }