#!/usr/bin/python

#import ipaddress
import sys
import easysnmp
import subprocess

from easysnmp import Session as SNMPSession
from netmiko import ConnectHandler
from ops import log

class Session(object):
    
    def snmp(self, switch):
        try:
            session = SNMPSession(hostname = switch, community = 'moss', version = 1, use_sprint_value = True)
        except easysnmp.exceptions.EasySNMPConnectionError as e:
            log.error('Unable to establish an SNMP session with {}'.format(switch))
            sys.exit()
        except easysnmp.exceptions.EasySNMPTimeoutError as e:
            log.error('SNMP connection to {} timed out'.format(switch))
            sys.exit()
            
        log.info('Established connection with {}'.format(switch))
        return session


    def ssh(self, switch):
        try:
            session = ConnectHandler(
                device_type = 'linux',
                ip = switch,
                username = 'root',
                password = 'moss-test'
            )
        except:
            log.error('Unable to establish connection with {}'.format(switch))
            sys.exit()
            
        return session
    
    
    def ssh_with_specific_port(self, switch, port):
        try:
            session = ConnectHandler(
                device_type = 'linux',
                ip = switch,
                port = port,
                username = 'root',
                password = 'moss-test'
            )
        except:
            log.error('Unable to establish connection with {}'.format(switch))
            sys.exit()
            
        log.info('Established connection with {}'.format(switch))
        return session
        
        
    def scp_quagga_configuration_file(self, file, target, port):
        if port != 22:
            command = 'scp -P {} {}Quagga.conf root@{}:/etc/quagga/Quagga.conf'.format(port, file, target)
        else:
            command = 'scp {}Quagga.conf root@{}:/etc/quagga/Quagga.conf'.format(file, target)
            
        subprocess_command = command.split()
        process = subprocess.Popen(subprocess_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        
        if not out and not err:
            return {
                "status": "ok"
            }
        
        return {
            "status": "fail",
            "reason": err
        }
    
    
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