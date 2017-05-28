#!/usr/bin/python

import sys
import json

from ops import log
from ops.connection import Session


def _get_detail_json(switch, port):
    session = Session().snmp(switch)
    lldpLocSysName = session.get('.1.0.8802.1.1.2.1.3.3.0')
    lldpLocSysDesc = session.get('.1.0.8802.1.1.2.1.3.4.0')
    lldpLocPortDes = [element.value for element in session.walk('.1.0.8802.1.1.2.1.3.7.1.4')]
    lldpLocPortMac = [element.value for element in session.walk('.1.0.8802.1.1.2.1.3.7.1.3')]
    lldpRemSysName = [element.value for element in session.walk('.1.0.8802.1.1.2.1.4.1.1.9')]
    lldpRemSysDesc = [element.value for element in session.walk('.1.0.8802.1.1.2.1.4.1.1.10')]
    lldpRemPortDes = [element.value for element in session.walk('.1.0.8802.1.1.2.1.4.1.1.8')]
    lldpRemPortMac = [element.value for element in session.walk('.1.0.8802.1.1.2.1.4.1.1.7')]
    
    lldp_detail = {"detail": {
                    "local_system": {
                        "sys_name": lldpLocSysName.value[1:-1],
                        "sys_desc": lldpLocSysDesc.value[1:-1]
                    },
                    "neighbors": []
                    }               
                }  

    for index, remote in enumerate(lldpLocPortDes):
        try:
            if port == 0:
                lldp_detail["detail"]["neighbors"].append({
                    "local": {
                        "desc": remote[1:-1],
                        "mac": ':'.join(lldpLocPortMac[index][1:-1].split())
                    },
                    "remote": {
                        "sys_name": lldpRemSysName[index],
                        "sys_desc": lldpRemSysDesc[index],
                        "port": {
                            "desc": lldpRemPortDes[index],
                            "mac": lldpRemPortMac[index]
                        }
                    }
                })
            else:
                if remote[1:-1] == port:
                    lldp_detail["detail"]["neighbors"].append({
                        "local": {
                            "desc": remote[1:-1],
                            "mac": ':'.join(lldpLocPortMac[index][1:-1].split())
                        },
                        "remote": {
                            "sys_name": lldpRemSysName[index],
                            "sys_desc": lldpRemSysDesc[index],
                            "port": {
                                "desc": lldpRemPortDes[index],
                                "mac": lldpRemPortMac[index]
                            }
                        }
                    })
        except:
            lldp_detail["detail"]["neighbors"].append({
                "local": {
                    "desc": remote[1:-1],
                    "mac": ':'.join(lldpLocPortMac[index][1:-1].split())
                },
                "remote": {
                    "sys_name": "None",
                    "sys_desc": "None",
                    "port": {
                        "desc": "None",
                        "mac": "None"
                    }
                }
            })

    return lldp_detail


def _print_detail_table(lldp_json):
        table_format = 'Local Port ID: {}\n\tLocal Sys Name: {}\n\t\tLocal Sys Desc: {}\n\t\tLocal Port MAC: {} \
                        \n\tRemote Sys Name: {}\n\t\tRemote Sys Desc: {}\n\t\tRemote Port Desc: {} \
                        \n\t\tRemote Port MAC: {}\n'
        print ''
        for neighbor in lldp_json["detail"]["neighbors"]:
            print table_format.format(neighbor["local"]["desc"], lldp_json["detail"]["local_system"]["sys_name"], 
                                      lldp_json["detail"]["local_system"]["sys_desc"], neighbor["local"]["mac"],
                                      neighbor["remote"]["sys_name"], neighbor["remote"]["sys_name"], 
                                      neighbor["remote"]["port"]["desc"], neighbor["remote"]["port"]["mac"])
        print ''
    

def _get_info_json(switch):
    session = Session().snmp(switch)
    lldpTxInt = session.get('.1.0.8802.1.1.2.1.1.1.0')
    lldpTxHold = session.get('.1.0.8802.1.1.2.1.1.2.0')
    lldpInitDel = session.get('.1.0.8802.1.1.2.1.1.3.0')
    lldpTxDel = session.get('.1.0.8802.1.1.2.1.1.4.0')
    lldpNotIn = session.get('.1.0.8802.1.1.2.1.1.5.0')
    
    lldpTblIns = session.get('.1.0.8802.1.1.2.1.2.2.0')
    lldpTblDel = session.get('.1.0.8802.1.1.2.1.2.3.0')
    lldpTblDrp = session.get('.1.0.8802.1.1.2.1.2.4.0')
    lldpTblAgO = session.get('.1.0.8802.1.1.2.1.2.5.0')
    
    lldpPorts = [element.value for element in session.walk('.1.0.8802.1.1.2.1.3.7.1.4')]
    lldpTxTot = [element.value for element in session.walk('.1.0.8802.1.1.2.1.2.6.1.2')]
    lldpRxTot = [element.value for element in session.walk('.1.0.8802.1.1.2.1.2.7.1.4')]
    lldpRxErr = [element.value for element in session.walk('.1.0.8802.1.1.2.1.2.7.1.3')]
    lldpRxDrp = [element.value for element in session.walk('.1.0.8802.1.1.2.1.2.7.1.2')]
    lldpRxTlvDrp = [element.value for element in session.walk('.1.0.8802.1.1.2.1.2.7.1.5')]
    lldpRxTlvUnr = [element.value for element in session.walk('.1.0.8802.1.1.2.1.2.7.1.6')]
    lldpRxAgTot = [element.value for element in session.walk('.1.0.8802.1.1.2.1.2.7.1.7')]

    lldp_info = {"info": {
                    "general": {
                        "tx_int": lldpTxInt.value,
                        "tx_hold": lldpTxHold.value,
                        "tx_del": lldpTxDel.value,
                        "reinit_del": lldpInitDel.value,
                        "notif_int": lldpNotIn.value
                    },
                    "table": {
                        "inserts": lldpTblIns.value,
                        "deletes": lldpTblDel.value,
                        "drops": lldpTblDrp.value,
                        "age_outs": lldpTblAgO.value
                    },
                    "neighbors": []
                }
            }

    for index, port in enumerate(lldpPorts):
        lldp_info["info"]["neighbors"].append({
            "port_id": port[1:-1],
            "tx_ok": lldpTxTot[index],
            "rx_ok": lldpRxTot[index],
            "rx_err": lldpRxErr[index],
            "rx_drp": lldpRxDrp[index],
            "rx_tlv_drp": lldpRxTlvDrp[index],
            "rx_tlv_unr": lldpRxTlvUnr[index],
            "rx_tlv_ag": lldpRxAgTot[index]
        })

    return lldp_info


def _get_neighbors_json(switch, port):
    session = Session().snmp(switch)
    lldpLocSysName = session.get('.1.0.8802.1.1.2.1.3.3.0')
    lldpLocPortDes = [element.value for element in session.walk('.1.0.8802.1.1.2.1.3.7.1.4')]
    lldpLocPortMac = [element.value for element in session.walk('.1.0.8802.1.1.2.1.3.7.1.3')]
    lldpRemSysName = [element.value for element in session.walk('.1.0.8802.1.1.2.1.4.1.1.9')]
    lldpRemPortDes = [element.value for element in session.walk('.1.0.8802.1.1.2.1.4.1.1.8')]
    lldpRemPortMac = [element.value for element in session.walk('.1.0.8802.1.1.2.1.4.1.1.7')]
    
    lldp_neighbors = {"neighbors": []}

    for index, neighbor in enumerate(lldpLocPortDes):
        try:
            if port == 0:
                lldp_neighbors["neighbors"].append({
                    "local": {
                        "sys_name": lldpLocSysName.value[1:-1],
                        "port_id": lldpLocPortDes[index][1:-1],
                        "mac": ':'.join(lldpLocPortMac[index][1:-1].split())
                    },
                    "remote": {
                        "sys_name": lldpRemSysName[index][1:-1],
                        "port_id": lldpRemPortDes[index][1:-1],
                        "mac": ':'.join(lldpRemPortMac[index][1:-1].split())
                    }
                })
            else:
                if neighbor[1:-1] == port:
                    lldp_neighbors["neighbors"].append({
                        "local": {
                            "sys_name": lldpLocSysName.value[1:-1],
                            "port_id": lldpLocPortDes[index][1:-1],
                            "mac": ':'.join(lldpLocPortMac[index][1:-1].split())
                        },
                        "remote": {
                            "sys_name": lldpRemSysName[index][1:-1],
                            "port_id": lldpRemPortDes[index][1:-1],
                            "mac": ':'.join(lldpRemPortMac[index][1:-1].split())
                        }
                    })
        except:
            lldp_neighbors["neighbors"].append({
                "local": {
                    "sys_name": lldpLocSysName.value[1:-1],
                    "port_id": lldpLocPortDes[index][1:-1],
                    "mac": ':'.join(lldpLocPortMac[index][1:-1].split())
                },
                "remote": {
                    "sys_name": "None",
                    "port_id": "None",
                    "mac": "None"
                }
            })

    return lldp_neighbors


def _print_neighbors_table(lldp_json):
    table_format = '{:<20} {:<10} {:<25} {:<20} {:<10} {}'
          
    print ''
    print table_format.format('Local Sys', 'Port ID', 'Link layer', 'Remote Sys', 'Port ID', 'Link layer')
        
    for neighbor in lldp_json["neighbors"]:
        print table_format.format(neighbor["local"]["sys_name"], neighbor["local"]["port_id"], 
                                  neighbor["local"]["mac"], neighbor["remote"]["sys_name"], 
                                  neighbor["remote"]["port_id"], neighbor["remote"]["mac"])
    print ''


def get_ports_detail(switch, json_output):
    lldp_json = _get_detail_json(switch, 0)
    
    if json_output:
        print json.dumps(lldp_json, sort_keys=True, indent=4, separators=(',', ': '))
    else:
        _print_detail_table(lldp_json)


def get_port_detail(switch, json_output, port):
    lldp_json = _get_detail_json(switch, port)
    
    if json_output:
        print json.dumps(lldp_json, sort_keys=True, indent=4, separators=(',', ': '))
    else:
        _print_detail_table(lldp_json)


def get_info(switch, json_output):
    lldp_json = _get_info_json(switch)
    
    if json_output:
        print json.dumps(lldp_json, sort_keys=True, indent=4, separators=(',', ': '))
    else:
        print ''
        print 'Tx interval: {}'.format(lldp_json["info"]["general"]["tx_int"])
        print 'Tx hold: {}'.format(lldp_json["info"]["general"]["tx_hold"])
        print 'Tx delay: {}'.format(lldp_json["info"]["general"]["tx_del"])
        print 'Reinit delay: {}'.format(lldp_json["info"]["general"]["reinit_del"])
        print 'Notification interval: {}'.format(lldp_json["info"]["general"]["notif_int"])
        
        print ''
        print 'Remote table inserts: {}'.format(lldp_json["info"]["table"]["inserts"])
        print 'Remote table deletes: {}'.format(lldp_json["info"]["table"]["deletes"])
        print 'Remote table drops: {}'.format(lldp_json["info"]["table"]["drops"])
        print 'Remote table age outes: {}'.format(lldp_json["info"]["table"]["age_outs"])
        
        table_format = '{:<10} {:<10} {:<10} {:<10} {:<10} {:<15} {:<17} {}'
        print ''
        print table_format.format('Port ID', 'Tx_ok', 'Rx_ok', 'Rx_err', 'Rx_drp', 'Rx TLV drp', 'Rx TLV unreco',
                                  'Rx TLV Age outs')
        
        for neighbor in lldp_json["info"]["neighbors"]:
            print table_format.format(neighbor["port_id"], neighbor["tx_ok"], neighbor["rx_ok"], 
                                      neighbor["rx_err"], neighbor["rx_drp"], neighbor["rx_tlv_drp"], 
                                      neighbor["rx_tlv_unr"], neighbor["rx_tlv_ag"])
        print ''
    
    
def get_neighbors(switch, json_output):
    lldp_json = _get_neighbors_json(switch, 0)
    
    if json_output:
        print json.dumps(lldp_json, sort_keys=True, indent=4, separators=(',', ': '))
    else:
        _print_neighbors_table(lldp_json)


def get_port_neighbor(switch, json_output, port):
    lldp_json = _get_neighbors_json(switch, port)

    if json_output:
        print json.dumps(lldp_json, sort_keys=True, indent=4, separators=(',', ': '))
    else:
        _print_neighbors_table(lldp_json)


def get_ports(switch, json_output):
    session = Session().snmp(switch)
    
    lldpPorts = [element.value for element in session.walk('.1.0.8802.1.1.2.1.3.7.1.4')]
    lldpPorts_json = {"ports": []}

    for port in lldpPorts:
        lldpPorts_json["ports"].append(port[1:-1])

    if json_output:
        print json.dumps(lldpPorts_json, sort_keys=True, indent=4, separators=(',', ': '))
    else:
        table_format = '{}'
        print ''
        print table_format.format('Port ID')

        for port in lldpPorts_json["ports"]:
            print table_format.format(port)

        print ''