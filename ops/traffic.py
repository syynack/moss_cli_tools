#!/usr/bin/python

import time
import click

from ops.connection import Session

def _get_traffic(switch):
	session = Session().snmp(switch)

	global if_desc, if_mtu, rx_bytes, tx_bytes, in_discards, out_discards, in_errors, out_errors
	if_desc = [element.value for element in session.walk('1.3.6.1.2.1.55.1.5.1.2')]
	if_mtu = [element.value for element in session.walk('1.3.6.1.2.1.2.2.1.4')]
	rx_bytes = [element.value for element in session.walk('1.3.6.1.2.1.2.2.1.10')]
	tx_bytes = [element.value for element in session.walk('1.3.6.1.2.1.2.2.1.16')]
	in_discards = [element.value for element in session.walk('1.3.6.1.2.1.2.2.1.13')]
	out_discards = [element.value for element in session.walk('1.3.6.1.2.1.2.2.1.19')]
	in_errors = [element.value for element in session.walk('1.3.6.1.2.1.2.2.1.14')]
	out_errors = [element.value for element in session.walk('1.3.6.1.2.1.2.2.1.20')]


def _print_traffic_table():
	table_format = '{:<10} {:<10} {:<10} {:<10} {:<10} {:<10} {:<10} {}'
	print ''
	print table_format.format('Port ID', 'MTU', 'rx_ok', 'rx_drp', 'rx_err', 'tx_ok', 'tx_drp', 'tx_err')
	    
	for index, port in enumerate(if_desc):
   		print table_format.format(port.replace('"', ''), if_mtu[index], rx_bytes[index], in_discards[index],
   								  in_errors[index], tx_bytes[index], out_discards[index], out_errors[index])

	print ''


def _print_traffic_table_for_port(_port):
	table_format = '{:<10} {:<10} {:<10} {:<10} {:<10} {:<10} {:<10} {}'
	print ''
	print table_format.format('Port ID', 'MTU', 'rx_ok', 'rx_drp', 'rx_err', 'tx_ok', 'tx_drp', 'tx_err')
	    
	for index, port in enumerate(if_desc):
		if port.replace('"', '') == _port:
	   		print table_format.format(port.replace('"', ''), if_mtu[index], rx_bytes[index], in_discards[index],
	   								  in_errors[index], tx_bytes[index], out_discards[index], out_errors[index])

	print ''


def watch_traffic(switch):
	while True:
		click.clear()
		_get_traffic(switch)
		_print_traffic_table()
		time.sleep(5)


def get_traffic_for_port(switch, port):
	_get_traffic(switch)
	_print_traffic_table_for_port(port)


def watch_traffic_for_port(switch, port):
	while True:
		click.clear()
		_get_traffic(switch)
		_print_traffic_table_for_port(port)
		time.sleep(5)


def get_traffic(switch):
	_get_traffic(switch)
	_print_traffic_table()