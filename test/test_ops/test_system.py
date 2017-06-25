#!/usr/bin/python

import json
import re

def _get_system_uptime_json(switch):
    command = 'uptime'
    output = '''
 22:02:48 up 18 min,  0 users,  load average: 0.07, 0.02, 0.03
    '''
    
    output_dict = {}
    regex = r'\s(?P<current_time>[0-9]{2}:[0-9]{2}:[0-9]{2})\sup\s(?P<uptime>[^\s]+\s[^,]+).*(?P<users>[0-9])\suser.*load\saverage:\s(?P<avg_1_min_load>[0-100].[0-9]{2}),\s(?P<avg_5_min_load>[0-100].[0-9]{2}),\s(?P<avg_15_min_load>[0-100].[0-9]{2})'
    
    for line in output.splitlines():
        data = re.search(regex, line)
        if data is not None:
            output_dict.update(data.groupdict())
    
    return output_dict


def _get_system_info_json(switch):
    command = 'uname -s -n -r -m -p -i -o'
    output = '''
Linux d1-p1-l1-r1 4.4.0-31-generic x86_64 unknown unknown GNU/Linux
    '''
    
    output = output.split()
    
    output_dict = {
        "kernel_name": output[0],
        "hostname": output[1],
        "kernel_release": output[2],
        "architecture": output[3],
        "processor": output[4],
        "hardware_platform": output[5],
        "operating_system": output[6]
    }
    
    return output_dict


def get_system_uptime_in_json(switch):
    output = _get_system_uptime_json(switch)
    
    print json.dumps(output, sort_keys=True, indent=4, separators=(',', ': '))


def get_system_uptime(switch):
    output = _get_system_uptime_json(switch)
    
    print ''
    print 'Uptime: {}'.format(output['uptime'])
    print ''


def get_system_info_in_json(switch):
    output = _get_system_info_json(switch)
    
    print json.dumps(output, sort_keys=True, indent=4, separators=(',', ': '))


def get_system_info(switch):
    output = _get_system_info_json(switch)
    
    table_format = '{:<15} {:<15} {:<10} {:<12} {:<16} {:<10} {}'
    
    print ''
    print table_format.format('Hostname', 'Architecture', 'OS', 'Kernel Name', 'Kernel Release', 'Processor', 'Hardware Platform')
    print table_format.format(output['hostname'], output['architecture'], output['operating_system'], output['kernel_name'],
        output['kernel_release'], output['processor'], output['hardware_platform']
    )
    
    print ''