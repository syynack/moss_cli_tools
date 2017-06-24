#!/usr/bin/python

import sys
import time

from difflib import unified_diff as diff
from ops import log
from ops.connection import Session

def _get_config(switch):
	session = Session().ssh(switch)

	command = 'vtysh -c "show running-config"'
	log.info('Retrieving current running config from {}'.format(switch))
	running_config = session.send_command(command)
	log.info('{} config retrieved'.format(switch))

	return running_config


def _send_diff_to_file(switch, remote_switch, diff1, diff2, output_file):
    log.info('Writing config diff to file {}'.format(output_file))
    tofile = '{} running configuration'.format(switch)
    fromfile = '{} running configuration'.format(remote_switch)
    
    with open(output_file, 'w') as output_file:
        for line in diff(diff1.splitlines(), diff2.splitlines(), tofile=tofile, fromfile=fromfile, lineterm=''):
            output_file.write(line + '\n')


def _print_diff(switch, remote_switch, diff1, diff2):
    tofile = '{} running configuration'.format(switch)
    fromfile = '{} running configuration'.format(remote_switch)
    
    print ''
    
    for line in diff(diff1.splitlines(), diff2.splitlines(), tofile=tofile, fromfile=fromfile, lineterm=''):
		if line[0] == '+':
			print '\033[32m' + line + '\033[0m'
		elif line[0] == '-':
			print '\033[31m' + line + '\033[0m'
		else:
			print line
            
    print ''


def get_running_config(switch, output_file):
	running_config = _get_config(switch)

	if output_file:
		log.info('Writing running config to file {}'.format(output_file))
		with open(output_file, 'w') as config_file:
			config_file.write(running_config)
	else:
		print ''
		print running_config
		print ''


def diff_config_file(switch, diff_file, output_file):
	running_config = _get_config(switch)

	with open(diff_file, 'r') as read_diff_file:
		file_to_diff = read_diff_file.read()

	log.info('Diffing {} running configuration against {}'.format(switch, diff_file))
	if output_file:
		_send_diff_to_file(switch, diff_file, running_config, file_to_diff, output_file)
	else:
		_print_diff(switch, diff_file, running_config, file_to_diff)


def diff_config_switch(switch, remote_switch, output_file):
	local_running_config = _get_config(switch)
	remote_running_config = _get_config(remote_switch)

	log.info('Getting config differences between {} and {}'.format(switch, remote_switch))
	if output_file:
		_send_diff_to_file(switch, remote_switch, local_running_config, remote_running_config, output_file)
	else:
		_print_diff(switch, remote_switch, local_running_config, remote_running_config)
        
        
def reload(switch):
    session = Session().ssh(switch)
    reload_output = session.send_command('/etc/init.d/quagga force-reload')
    
    log.info('Command sent. Waiting 5 seconds to check status')
    time.sleep(5)
    confirmation_output = session.send_command('ps -ef | grep quagga')
    
    result = confirmation_output.splitlines()
        
    if len(result) < 2:
        log.error('Restart of Quagga on {} was unsuccessful!'.format(target))
        sys.exit()
    
    log.info('Quagga.conf reload successful')           