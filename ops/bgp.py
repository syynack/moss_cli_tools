#!/usr/bin/python

import json

from ops.connection import Session

BGP_NEIGHBOR_ESTABLISHED_TEMPLATE = '''
Neighbor {} address is {} with remote AS {} and is a member of {}
  Current State is {} and has been for {}
  BGP version is {}, {}'s Router ID is {}
  Hold time is {}, keepalive time is {}
  Message advertisement runs is {}
  Connect retry timer is {}

  Total connections established is {}
  Total connections dropped is {}
  Session was last reset {} ago due to a {} with code {}

  Messages
                              Sent            Received
          Open:               {}              {}
          Notification:       {}              {}    
          Update:             {}              {}
          Keepalive:          {}              {}
          Router Refesh:      {}              {}
          Capability:         {}              {}
          Total:              {}              {}
          
  Local IPv6 address is {} using port {}
  Remote IPv6 address is {} using port {}
  Next hop is {}
  Nexthop global is {}
  Nexthop local is {}
  
  BFD detect multiplier is {}
  BFD minimum RX interval is {}
  BFD minimum TX interval is {}
'''

BGP_NEIGHBOR_NOT_ESTABLISHED_TEMPLATE = '''
Neighbor {} with remote AS {}
  Current State is {}
  BGP version is {}, {}'s Router ID is {}
  Hold time is {}, keepalive time is {}
  Message advertisement runs is {}
  Connect retry timer is {}
'''

def _get_bgp_memory_json(switch):
    session = Session().ssh(switch)
    
    command = 'vtysh -c "show bgp memory"'
    bgp_memory_output = session.send_command(command)
    bgp_memory_json = {"tables": []}
    
    for line in bgp_memory_output.splitlines():
        line = line.split(',')
        table_details = line[0].split()
        memory_usage = line[1].split()
        
        if memory_usage[3] == 'KiB':
            memory_usage[2] = int(memory_usage[2]) * 1024
        
        bgp_memory_json["tables"].append({
            "table_id": '_'.join(table_details[1:]).lower().replace('-', '_'),
            "total": table_details[0],
            "mem_usage": str(memory_usage[2])
        })
        
    return bgp_memory_json


def _get_bgp_neighbors_json(switch):
    session = Session().ssh(switch)
    
    command = 'vtysh -c "show bgp neighbors json"'
    bgp_neighbors_json = session.send_command(command)
    
    return json.loads(bgp_neighbors_json)


def _print_bgp_neighbor(bgp_neighbors_json, peer):
    if bgp_neighbors_json[peer]["bgpState"] == 'Established':
        print BGP_NEIGHBOR_ESTABLISHED_TEMPLATE.format(
            bgp_neighbors_json[peer]["hostname"], peer, bgp_neighbors_json[peer]["remoteAs"],
            bgp_neighbors_json[peer]["peerGroup"], bgp_neighbors_json[peer]["bgpState"],
            bgp_neighbors_json[peer]["bgpTimerUpString"], bgp_neighbors_json[peer]["bgpVersion"],
            bgp_neighbors_json[peer]["hostname"], bgp_neighbors_json[peer]["remoteRouterId"],
            int(bgp_neighbors_json[peer]["bgpTimerHoldTimeMsecs"]) / 1000,
            int(bgp_neighbors_json[peer]["bgpTimerKeepAliveIntervalMsecs"]) / 1000,
            int(bgp_neighbors_json[peer]["minBtwnAdvertisementRunsTimerMsecs"]) / 1000,
            bgp_neighbors_json[peer]["connectRetryTimer"], bgp_neighbors_json[peer]["connectionsEstablished"],
            bgp_neighbors_json[peer]["connectionsDropped"], 
            'None' if not bgp_neighbors_json[peer].get("lastResetTimerMsecs") else int(bgp_neighbors_json[peer]["lastResetTimerMsecs"]) / 1000,
            'None' if not bgp_neighbors_json[peer].get("lastResetDueTo") else bgp_neighbors_json[peer]["lastResetDueTo"],
            'None' if not bgp_neighbors_json[peer].get("lastErrorCodeSubcode") else bgp_neighbors_json[peer]["lastErrorCodeSubcode"], 
            bgp_neighbors_json[peer]["messageStats"]["opensSent"], bgp_neighbors_json[peer]["messageStats"]["opensRecv"],
            bgp_neighbors_json[peer]["messageStats"]["notificationsSent"],
            bgp_neighbors_json[peer]["messageStats"]["notificationsRecv"],
            bgp_neighbors_json[peer]["messageStats"]["updatesSent"], bgp_neighbors_json[peer]["messageStats"]["updatesRecv"],
            bgp_neighbors_json[peer]["messageStats"]["keepalivesSent"], bgp_neighbors_json[peer]["messageStats"]["keepalivesRecv"],
            bgp_neighbors_json[peer]["messageStats"]["routeRefreshSent"],
            bgp_neighbors_json[peer]["messageStats"]["routeRefreshRecv"],
            bgp_neighbors_json[peer]["messageStats"]["capabilitySent"],
            bgp_neighbors_json[peer]["messageStats"]["capabilityRecv"],
            bgp_neighbors_json[peer]["messageStats"]["totalSent"], bgp_neighbors_json[peer]["messageStats"]["totalRecv"],
            bgp_neighbors_json[peer]["hostLocal"], bgp_neighbors_json[peer]["portLocal"],
            bgp_neighbors_json[peer]["hostForeign"], bgp_neighbors_json[peer]["portForeign"],
            bgp_neighbors_json[peer]["nexthop"], bgp_neighbors_json[peer]["nexthopGlobal"], bgp_neighbors_json[peer]["nexthopLocal"],
            bgp_neighbors_json[peer]["peerBfdInfo"]["detectMultiplier"], bgp_neighbors_json[peer]["peerBfdInfo"]["rxMinInterval"],
            bgp_neighbors_json[peer]["peerBfdInfo"]["txMinInterval"]
        )
    else:
        print BGP_NEIGHBOR_NOT_ESTABLISHED_TEMPLATE.format(
            peer, bgp_neighbors_json[peer]["remoteAs"],
            bgp_neighbors_json[peer]["bgpState"],
            bgp_neighbors_json[peer]["bgpVersion"],
            peer, bgp_neighbors_json[peer]["remoteRouterId"],
            int(bgp_neighbors_json[peer]["bgpTimerHoldTimeMsecs"]) / 1000,
            int(bgp_neighbors_json[peer]["bgpTimerKeepAliveIntervalMsecs"]) / 1000,
            int(bgp_neighbors_json[peer]["minBtwnAdvertisementRunsTimerMsecs"]) / 1000,
            bgp_neighbors_json[peer]["connectRetryTimer"]
        )
    
    
def _get_bgp_summary_json(switch):
    session = Session().ssh(switch)
    
    command = 'vtysh -c "show bgp summary json"'
    bgp_summary_json = session.send_command(command)
    return bgp_summary_json


def get_bgp_memory_usage_in_json(switch):
    bgp_memory_json = _get_bgp_memory_json(switch)
    print json.dumps(bgp_memory_json, sort_keys=True, indent=4, separators=(',', ': '))


def get_bgp_memory_usage(switch):
    bgp_memory_json = _get_bgp_memory_json(switch)
    
    table_format = '{:<25} {:<18} {}'
    print table_format.format('Table ID', 'Total Entries', 'Memory Usage (Bytes)')
    
    for table in bgp_memory_json["tables"]:
        print table_format.format(table["table_id"], table["total"], table["mem_usage"])
        

def get_bgp_specific_neighbor_in_json(switch, neighbor):
    bgp_neighbors_json = _get_bgp_neighbors_json(switch)
    for peer in bgp_neighbors_json:
        if peer == neighbor:
            print json.dumps(bgp_neighbors_json[peer], sort_keys=True, indent=4, separators=(',', ': '))
    

def get_bgp_specific_neighbor(switch, neighbor):
    bgp_neighbors_json = _get_bgp_neighbors_json(switch)
    
    for peer in bgp_neighbors_json:
        if peer == neighbor:
            _print_bgp_neighbor(bgp_neighbors_json, peer)


def get_bgp_neighbors_in_json(switch):
    bgp_neighbors_json = _get_bgp_neighbors_json(switch)
    print json.dumps(bgp_neighbors_json, sort_keys=True, indent=4, separators=(',', ': '))


def get_bgp_neighbors(switch):
    bgp_neighbors_json = _get_bgp_neighbors_json(switch)
    
    for peer in bgp_neighbors_json:
        _print_bgp_neighbor(bgp_neighbors_json, peer)


def get_bgp_summary_in_json(switch):
    bgp_summary_json = json.loads(_get_bgp_summary_json(switch))
    print json.dumps(bgp_summary_json, sort_keys=True, indent=4, separators=(',', ': '))
    

def get_bgp_summary(switch):
    bgp_summary_json = json.loads(_get_bgp_summary_json(switch))
    
    print ''
    print '  Local Router ID: {}'.format(bgp_summary_json.get('routerId'))
    print ''
    
    table_format = '{:<20} {:<20} {:<12} {:<12} {:<8} {:<4} {:<8} {:<8} {:<8} {:<10} {:<10} {:<8} {}'
    print table_format.format('IPv6 Address', 'Hostname', 'State', 'Remote AS', 'Type', 'V', 'msgRecv', 'msgSent',
                              'Table V', 'UP/DOWN', 'Prefixes', 'inQ', 'outQ')
    
    for peer in bgp_summary_json["peers"]:
        print table_format.format(peer, bgp_summary_json["peers"][peer].get('hostname'), 
                                  bgp_summary_json["peers"][peer]["state"], bgp_summary_json["peers"][peer]["remoteAs"],
                                  bgp_summary_json["peers"][peer]["idType"], bgp_summary_json["peers"][peer]["version"],
                                  bgp_summary_json["peers"][peer]["msgRcvd"], bgp_summary_json["peers"][peer]["msgSent"],
                                  bgp_summary_json["peers"][peer]["tableVersion"],
                                  bgp_summary_json["peers"][peer]["peerUptime"],
                                  bgp_summary_json["peers"][peer]["prefixReceivedCount"],
                                  bgp_summary_json["peers"][peer]["inq"], bgp_summary_json["peers"][peer]["outq"])
    
    print ''
    print '  RIB Count: {}'.format(bgp_summary_json.get("ribCount"))
    print '  RIB Memory: {}'.format(bgp_summary_json.get("ribMemory"))
    print '  Total peers: {}'.format(bgp_summary_json.get("totalPeers"))
    print ''