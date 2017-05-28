#!/usr/bin/python

import ipaddress
import sys

from easysnmp import Session as SNMPSession
from netmiko import ConnectHandler
from ops import log

class Session(object):
    
    def snmp(self, switch):
        session = SNMPSession(hostname = switch, community = 'moss', version = 1, use_sprint_value = True)
        log.debug('Established connection with {}'.format(switch))
        return session


    def ssh(self, switch):
        try:
            session = ConnectHandler(
                device_type = 'linux',
                ip = switch,
                username = 'root',
                password = 'moss'
            )
        except:
            log.error('Unable to establish connection with {}'.format(switch))
            sys.exit()
            
        log.debug('Established connection with {}'.format(switch))
        return session


def V6Format(address):
    address = address.split('2.16.')
    address = address[1].split('.')
    address = address[0:16]
    
    for index, byte in enumerate(address):
        if str(byte) == '0':
            address[index] = '00'
        else:
            if len(str(byte)) == 1:
                address[index] = '0' + format(int(byte), 'x') 
            else:
                address[index] = format(int(byte), 'x')
    
    address = ''.join(address)
    address = ':'.join([address[i:i+4] for i in range(0, len(address), 4)])
    return str(ipaddress.ip_address(unicode(address)))