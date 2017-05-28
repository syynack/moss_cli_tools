#!/usr/bin/python

'''
leaf_template_file = 'leaf_config_template.j2'
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader('/etc/moss/switch/config/'),
                               trim_blocks = True,
                               lstrip_blocks = True)
leaf_template = jinja_env.get_template(leaf_template_file)
ports = subprocess.Popen(["vtysh -c 'show int d' | awk '{print $1}' | sed 's/Interface//g' | grep eth"], shell=True, stdout=subprocess.PIPE)
stdout, stderr = ports.communicate()

switch = [{
            'hostname': hostname,
            'uplink': uplink_prefix,
            'downlink': downlink_prefix,
            'rid': rid,
            'type': type,
            'ports': port_list
        }]
        
    now = datetime.now()
    output_filename = '{}-leaf_{}:{}:{}_{}-{}-{}[{}].json'.format(hostname, now.hour, now.minute, now.second, now.day, now.month, now.year, getpass.getuser())
        
    with open(output_filename, 'w') as config_json_output:
        for config_parameter in switch:
            config_result = leaf_template.render(config_parameter)
            config_json_output.write(config_result)
'''

import jinja2

def generate_clos(port_count, prefix, tor_count):
	pass