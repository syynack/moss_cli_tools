#!/usr/bin/python

import json

from ops import log
from ops.connection import Session

def _get_brief_json(switch, port):
    session = Session().snmp(switch)
    
    portId = [element.value for element in session.walk('.1.3.6.1.2.1.55.1.5.1.2')]
    admin = [element.value for element in session.walk('.1.3.6.1.2.1.55.1.5.1.9')]
    oper = [element.value for element in session.walk('.1.3.6.1.2.1.55.1.5.1.10')]
  
    ports_json = {"ports": []}

    for index, port_id in enumerate(portId):
        if port == 0:
            ports_json["ports"].append({
                "port_id": port_id.replace('"', ''),
                "admin": admin[index].replace('1', 'up').replace('0', 'down'),
                "oper": oper[index].replace('1', 'up').replace('0', 'down')
            })
        else:
            if port_id == port:
                ports_json["ports"].append({
                    "port_id": port_id.replace('"', ''),
                    "admin": admin[index].replace('1', 'up').replace('0', 'down'),
                    "oper": oper[index].replace('1', 'up').replace('0', 'down')
                })
                
    return ports_json


def _print_brief_table(port_brief_json):
    table_format = '{:<10} {:<10} {}'
    print ''
    print table_format.format('Port ID', 'Admin', 'Oper')
        
    for port in port_brief_json["ports"]:
        print table_format.format(port["port_id"], port["admin"], port["oper"])

    print ''


def _get_desc_json(switch, _port):
    session = Session().ssh(switch)
    
    command = 'vtysh -c "show interface description" | tail -n +2'
    port_desc = session.send_command(command)
    port_desc = port_desc.splitlines()
    
    ports_json = {"ports": []}
    
    for index, port in enumerate(port_desc):
        port = port.split()
        if _port == 0:
            if len(port) < 4:
                ports_json["ports"].append({
                    "port_id": port[0],
                    "admin": port[1],
                    "oper": port[2],
                    "desc": "None"
                })
            elif len(port) >= 4:
                ports_json["ports"].append({
                    "port_id": port[0],
                    "admin": port[1],
                    "oper": port[2],
                    "desc": port[3] 
                })
        else:
            if _port == port[0]:
                if len(port) < 4:
                    ports_json["ports"].append({
                        "port_id": port[0],
                        "admin": port[1],
                        "oper": port[2],
                        "desc": "None"
                    })
                elif len(port) >= 4:
                    ports_json["ports"].append({
                        "port_id": port[0],
                        "admin": port[1],
                        "oper": port[2],
                        "desc": port[3] 
                    })
                     
    return ports_json


def _print_desc_table(port_desc_json):
    table_format = '{:<10} {:<10} {:<10} {}'
    print ''
    print table_format.format('Port ID', 'Admin', 'Oper', 'Description')
        
    for port in port_desc_json["ports"]:
        print table_format.format(port["port_id"], port["admin"], port["oper"], port["desc"])
    
    print ''
    
    
def _get_detail_json(switch, _port):
    session = Session().snmp(switch)
    
    ifDesc = [element.value for element in session.walk('.1.3.6.1.2.1.55.1.5.1.2')]
    admin = [element.value for element in session.walk('.1.3.6.1.2.1.55.1.5.1.9')]
    oper = [element.value for element in session.walk('.1.3.6.1.2.1.55.1.5.1.10')]
    ifMtu = [element.value for element in session.walk('.1.3.6.1.2.1.2.2.1.4')]
    ifSpeed = [element.value for element in session.walk('.1.3.6.1.2.1.2.2.1.5')]
    ifMac = [element.value for element in session.walk('.1.3.6.1.2.1.2.2.1.6')]
    ifType = [element.value for element in session.walk('.1.3.6.1.2.1.2.2.1.3')]
    
    ports_json = {"ports": []}
    
    for index, port in enumerate(ifDesc):
        if _port == 0:
            ports_json["ports"].append({
                "port_id": port.replace('"', ''),
                "admin": admin[index].replace('1', 'up').replace('0', 'down'),
                "oper": oper[index].replace('1', 'up').replace('0', 'down'),
                "mtu": ifMtu[index],
                "speed": str(int(ifSpeed[index]) / 1000000),
                "ll_addr": ifMac[index],
                "type": ifType[index]
            })
        else:
            if port == _port:
                ports_json["ports"].append({
                    "port_id": port.replace('"', ''),
                    "admin": admin[index].replace('1', 'up').replace('0', 'down'),
                    "oper": oper[index].replace('1', 'up').replace('0', 'down'),
                    "mtu": ifMtu[index],
                    "speed": str(int(ifSpeed[index]) / 1000000),
                    "ll_addr": ifMac[index],
                    "type": ifType[index]
                })
            
    return ports_json


def _print_detail_table(port_detail_json):
    table_format = '{:<10} {:<8} {:<8} {:<8} {:<15} {:<18} {}'
    print ''
    print table_format.format('Port ID', 'Admin', 'Oper', 'MTU', 'Speed (Mb/s)', 'MAC', 'Type')
    
    for port in port_detail_json["ports"]:
        print table_format.format(port["port_id"], port["admin"], port["oper"], port["mtu"],
                                  port["speed"], port["ll_addr"], port["type"])
    
    print ''
    
    
def _get_stats_json(switch, _port):
    session = Session().snmp(switch)
    
    ifDesc = [element.value for element in session.walk('.1.3.6.1.2.1.55.1.5.1.2')]
    rxBytes = [element.value for element in session.walk('.1.3.6.1.2.1.2.2.1.10')]
    txBytes = [element.value for element in session.walk('.1.3.6.1.2.1.2.2.1.16')]
    ifInDiscards = [element.value for element in session.walk('.1.3.6.1.2.1.2.2.1.13')]
    ifOutDiscards = [element.value for element in session.walk('.1.3.6.1.2.1.2.2.1.19')]
    ifInErrors = [element.value for element in session.walk('.1.3.6.1.2.1.2.2.1.14')]
    ifOutErrors = [element.value for element in session.walk('.1.3.6.1.2.1.2.2.1.20')]
    
    ports_json = {"ports": []}
    
    for index, port in enumerate(ifDesc):
        if _port == 0:
            ports_json["ports"].append({
                "port_id": port.replace('"', ''),
                "rx": {
                    "ok": rxBytes[index],
                    "drp": ifInDiscards[index],
                    "err": ifInErrors[index]
                },
                "tx": {
                    "ok": txBytes[index],
                    "drp": ifOutDiscards[index],
                    "err": ifOutErrors[index]
                }
            })
        else:
            if port == _port:
                ports_json["ports"].append({
                    "port_id": port.replace('"', ''),
                    "rx": {
                        "ok": rxBytes[index],
                        "drp": ifInDiscards[index],
                        "err": ifInErrors[index]
                    },
                    "tx": {
                        "ok": txBytes[index],
                        "drp": ifOutDiscards[index],
                        "err": ifOutErrors[index]
                    }
                })
                
    return ports_json


def _print_stats_table(port_stats_json):
    table_format = '{:<10} {:<10} {:<10} {:<10} {:<10} {:<10} {}'
    print ''
    print table_format.format('Port ID', 'rx_ok', 'rx_drp', 'rx_err', 'tx_ok', 'tx_drp', 'tx_err')
    
    for port in port_stats_json["ports"]:
        print table_format.format(port["port_id"], port["rx"]["ok"], port["rx"]["drp"], port["rx"]["err"],
                                  port["tx"]["ok"], port["tx"]["drp"], port["tx"]["err"])
    
    print ''
            
    
def get_brief(switch, json_output):
    port_brief_json = _get_brief_json(switch, 0)
    
    if json_output:
        print json.dumps(port_brief_json, sort_keys=True, indent=4, separators=(',', ': '))
    else:
        _print_brief_table(port_brief_json)


def get_brief_port(switch, json_output, _port):
    port_brief_json = _get_brief_json(switch, _port)
    
    if json_output:
        print json.dumps(port_brief_json, sort_keys=True, indent=4, separators=(',', ': '))
    else:
        _print_brief_table(port_brief_json)


def get_desc(switch, json_output):
    port_desc_json = _get_desc_json(switch, 0)
    
    if json_output:
        print json.dumps(port_desc_json, sort_keys=True, indent=4, separators=(',', ': '))
    else:
        _print_desc_table(port_desc_json)
        
            
def get_desc_port(switch, json_output, _port):
    port_desc_json = _get_desc_json(switch, _port)
    
    if json_output:
        print json.dumps(port_desc_json, sort_keys=True, indent=4, separators=(',', ': '))
    else:
        _print_desc_table(port_desc_json)


def get_detail(switch, json_output):
    port_detail_json = _get_detail_json(switch, 0)
    
    if json_output:
        print json.dumps(port_detail_json, sort_keys=True, indent=4, separators=(',', ': '))
    else:
        _print_detail_table(port_detail_json)

    
def get_detail_port(switch, json_output, _port):
    port_detail_json = _get_detail_json(switch, _port)
    
    if json_output:
        print json.dumps(port_detail_json, sort_keys=True, indent=4, separators=(',', ': '))
    else:
        _print_detail_table(port_detail_json)


def get_stats(switch, json_output):
    port_stats_json = _get_stats_json(switch, 0)
    
    if json_output:
        print json.dumps(port_stats_json, sort_keys=True, indent=4, separators=(',', ': '))
    else:
        _print_stats_table(port_stats_json)
    
        
def get_stats_port(switch, json_output, _port):
    port_stats_json = _get_stats_json(switch, _port)
    
    if json_output:
        print json.dumps(port_stats_json, sort_keys=True, indent=4, separators=(',', ': '))
    else:
        _print_stats_table(port_stats_json)
