#!/usr/bin/python

import json

from ops.connection import Session

def get_environment(switch, json_output):
    session = Session().snmp(switch)
    
    sysuptime = session.get('.1.3.6.1.2.1.1.3.0')
    sysproc = [element.value for element in session.walk('.1.3.6.1.2.1.25.1.6')]
    sysusers = [element.value for element in session.walk('.1.3.6.1.2.1.25.1.5')]
    cpufivesec = session.get('.1.3.6.1.4.1.2021.10.1.3.1')
    cpumin = session.get('.1.3.6.1.4.1.2021.10.1.3.2')
    cpufivemin = session.get('.1.3.6.1.4.1.2021.10.1.3.3')
    ramtotal = session.get('.1.3.6.1.4.1.2021.4.5.0')
    raminuse = session.get('.1.3.6.1.4.1.2021.4.6.0')
    ramfree = int(ramtotal.value[:-3]) - int(raminuse.value[:-3])

    env_json = {"environment": {
                    "system": {
                        "uptime": sysuptime.value,
                        "processes": sysproc[0],
                        "users": sysusers[0]
                    }, 
                    "cpu": {
                        "usage": {
                            "five_sec": cpufivesec.value,
                            "min": cpumin.value,
                            "five_min": cpufivesec.value
                        }
                    }, 
                    "ram": {
                        "total": ramtotal.value[:-3],
                        "in_use": raminuse.value[:-3],
                        "free": str(ramfree)
                    }
                }
            }

    if json_output:
        print json.dumps(env_json, sort_keys=True, indent=4, separators=(',', ': '))
    else:
        processes = '\nProcesses\nUptime: {}\nProcesses: {}\nUsers: {}'
        cpu = '\nCPU Utilisation\n5 Sec:     {}\n1 Min:     {}\n5 Min:     {}'
        ram = '\nRAM\nTotal KB:  {}\nAvail KB:  {}\nUsed KB:   {}'
        print processes.format(env_json["environment"]["system"]["uptime"], 
                               env_json["environment"]["system"]["processes"], 
                               env_json["environment"]["system"]["users"])

        print cpu.format(env_json["environment"]["cpu"]["usage"]["five_sec"], 
                         env_json["environment"]["cpu"]["usage"]["min"], 
                         env_json["environment"]["cpu"]["usage"]["five_min"])

        print ram.format(env_json["environment"]["ram"]["total"], 
                         env_json["environment"]["ram"]["in_use"], 
                         env_json["environment"]["ram"]["free"])
        print ''
    
    
def get_info(switch, json_output):
    session = Session().snmp(switch)
    
    # System
    sysdescription = session.get('.1.3.6.1.2.1.1.1.0')
    syshostname = session.get('.1.3.6.1.2.1.1.5.0')
    sysuptime = session.get('.1.3.6.1.2.1.1.3.0')
    sysdev = [element.value for element in session.walk('1.3.6.1.2.1.25.3.2.1.3')]
    iftype = [element.value for element in session.walk('.1.3.6.1.2.1.2.2.1.2')]

    info_json = {"info": {
                    "description": sysdescription.value,
                    "hostname": syshostname.value,
                    "uptime": sysuptime.value,
                    "devices": [],
                }
            }
    for device in sysdev:
        info_json["info"]["devices"].append(device)

    if json_output:
        print json.dumps(info_json, sort_keys=True, indent=4, separators=(',', ': '))
    else:
        system = '\nHostname: {}\nDescription: {}\nUptime: {} Min\n'
        print system.format(info_json["info"]["hostname"], info_json["info"]["description"], 
                            info_json["info"]["uptime"])
        print 'System devices: '
        for device in info_json["info"]["devices"]:
            print device
        print ''
    
    
def get_memory(switch, json_output):
    session = Session().snmp(switch)
    
    dskid = [element.value for element in session.walk('.1.3.6.1.4.1.2021.9.1.3')]
    dsktotal = [element.value for element in session.walk('.1.3.6.1.4.1.2021.9.1.6')]
    dskavail = [element.value for element in session.walk('.1.3.6.1.4.1.2021.9.1.7')]
    dskused = [element.value for element in session.walk('.1.3.6.1.4.1.2021.9.1.8')]
    dskpath = [element.value for element in session.walk('1.3.6.1.4.1.2021.9.1.2')]

    memory_json = {"memory": []}
    for index, diskid in enumerate(dskid):
        memory_json["memory"].append(
            {
                "id": diskid,
                "total": str(int(dsktotal[index]) / 1000),
                "available": str(int(dskavail[index]) / 1000),
                "used": str(int(dskused[index]) / 1000),
                "mount_point": dskpath[index]
            }
        )
    
    if json_output:
        print json.dumps(memory_json, sort_keys=True, indent=4, separators=(',', ': '))
    else:
        table_format = '{:18} {:15} {:15} {:15} {}'
        print ''
        print table_format.format('ID', 'Total', 'Avail', 'Used', 'Mount point')
        for disk in memory_json["memory"]:
            print table_format.format(disk["id"], disk["total"], disk["available"], disk["used"], 
                                      disk["mount_point"])
        print ''