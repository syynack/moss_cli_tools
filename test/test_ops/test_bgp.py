#!/usr/bin/python

import json

from test_ops import test_utils as utils


def _get_bgp_memory_json(switch):
    command = 'vtysh -c "show bgp memory"'
    bgp_memory_output = '''
37 RIB nodes, using 5032 bytes of memory
6 BGP routes, using 672 bytes of memory
4 BGP route ancillaries, using 544 bytes of memory
1 Packets, using 56 bytes of memory
4 Adj-In entries, using 160 bytes of memory
2 Adj-Out entries, using 144 bytes of memory
16 Nexthop cache entries, using 1152 bytes of memory
7 BGP attributes, using 448 bytes of memory
7 BGP extra attributes, using 784 bytes of memory
1 BGP AS-PATH entries, using 40 bytes of memory
0 BGP AS-PATH segments, using 0 bytes of memory
19 peers, using 399 KiB of memory
1 peer groups, using 72 bytes of memory
492 hash tables, using 19 KiB of memory
3170 hash buckets, using 74 KiB of memory
    '''
    bgp_memory_json = {"tables": []}
    
    for line in bgp_memory_output.splitlines():
        line = line.split(',')
        
        if len(line) > 1:
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
    command = 'vtysh -c "show bgp neighbors json"'
    bgp_neighbors_json = '''
{
  "fd35:1:1:2::1":{
    "remoteAs":1,
    "localAs":1,
    "nbrInternalLink":true,
    "hostname":"d1-p1-l2-r1",
    "peerGroup":"ibgp_int_fabric",
    "bgpVersion":4,
    "remoteRouterId":"1.1.2.1",
    "bgpState":"Established",
    "bgpTimerUp":138000,
    "bgpTimerUpString":"00:02:18",
    "bgpTimerUpEstablishedEpoch":1498340876,
    "bgpTimerLastRead":8000,
    "bgpTimerLastWrite":77000,
    "bgpInUpdateElapsedTimeMsecs":77000,
    "bgpTimerHoldTimeMsecs":40000,
    "bgpTimerKeepAliveIntervalMsecs":13000,
    "neighborCapabilities":{
      "4byteAs":"advertisedAndReceived",
      "addPath":{
        "IPv6 Unicast":{
          "rxAdvertisedAndReceived":true
        }
      },
      "routeRefresh":"advertisedAndReceivedOldNew",
      "multiprotocolExtensions":{
        "IPv6 Unicast":{
          "advertisedAndReceived":true
        }
      },
      "gracefulRestart":"advertisedAndReceived",
      "gracefulRestartRemoteTimerMsecs":120000,
      "addressFamiliesByPeer":"none"
    },
    "gracefulRestartInfo":{
      "endOfRibSend":{
        "IPv6 Unicast":true
      },
      "endOfRibRecv":{
        "IPv6 Unicast":true
      }
    },
    "messageStats":{
      "depthInq":0,
      "depthOutq":0,
      "opensSent":2,
      "opensRecv":1,
      "notificationsSent":1,
      "notificationsRecv":0,
      "updatesSent":3,
      "updatesRecv":3,
      "keepalivesSent":11,
      "keepalivesRecv":10,
      "routeRefreshSent":0,
      "routeRefreshRecv":0,
      "capabilitySent":0,
      "capabilityRecv":0,
      "totalSent":17,
      "totalRecv":14
    },
    "minBtwnAdvertisementRunsTimerMsecs":1000,
    "addressFamilyInfo":{
      "IPv6 Unicast":{
        "peerGroupMember":"ibgp_int_fabric",
        "updateGroupId":1,
        "subGroupId":1,
        "packetQueueLength":0,
        "inboundSoftConfigPermit":true,
        "routerAlwaysNextHop":true,
        "commAttriSentToNbr":"extendedAndStandard",
        "acceptedPrefixCounter":2
      }
    },
    "connectionsEstablished":1,
    "connectionsDropped":0,
    "lastResetTimerMsecs":207000,
    "lastResetDueTo":"BGP Notification send",
    "lastErrorCodeSubcode":"0607",
    "lastNotificationReason":"Cease\/Connection collision resolution",
    "hostLocal":"fd35:1:1:1::1",
    "portLocal":179,
    "hostForeign":"fd35:1:1:2::1",
    "portForeign":34512,
    "nexthop":"1.1.1.1",
    "nexthopGlobal":"fd35:1:1:1::1",
    "nexthopLocal":"::",
    "bgpConnection":"nonSharedNetwork",
    "connectRetryTimer":2,
    "readThread":"on",
    "writeThread":"off"
  },
  "fd35:1:1:2::2":{
    "remoteAs":0,
    "localAs":1,
    "nbrExternalLink":true,
    "peerGroup":"ibgp_int_fabric",
    "bgpVersion":4,
    "remoteRouterId":"0.0.0.0",
    "bgpState":"Active",
    "bgpTimerLastRead":207000,
    "bgpTimerLastWrite":360000,
    "bgpInUpdateElapsedTimeMsecs":360000,
    "bgpTimerHoldTimeMsecs":40000,
    "bgpTimerKeepAliveIntervalMsecs":10000,
    "messageStats":{
      "depthInq":0,
      "depthOutq":0,
      "opensSent":0,
      "opensRecv":0,
      "notificationsSent":0,
      "notificationsRecv":0,
      "updatesSent":0,
      "updatesRecv":0,
      "keepalivesSent":0,
      "keepalivesRecv":0,
      "routeRefreshSent":0,
      "routeRefreshRecv":0,
      "capabilitySent":0,
      "capabilityRecv":0,
      "totalSent":0,
      "totalRecv":0
    },
    "minBtwnAdvertisementRunsTimerMsecs":1000,
    "addressFamilyInfo":{
      "IPv6 Unicast":{
        "peerGroupMember":"ibgp_int_fabric",
        "inboundSoftConfigPermit":true,
        "routerAlwaysNextHop":true,
        "commAttriSentToNbr":"extendedAndStandard",
        "acceptedPrefixCounter":0
      }
    },
    "connectionsEstablished":0,
    "connectionsDropped":0,
    "lastReset":"never",
    "connectRetryTimer":2,
    "nextConnectTimerDueInMsecs":1000,
    "readThread":"off",
    "writeThread":"off"
  }
}
    '''
    
    return json.loads(bgp_neighbors_json)


def _print_bgp_neighbor(bgp_neighbors_json, peer):
    if bgp_neighbors_json[peer]["bgpState"] == 'Established':
        print utils.get_bgp_neighbor_established(bgp_neighbors_json, peer)
    else:
        print utils.get_bgp_neighbor_not_established(bgp_neighbors_json, peer)
    
    
def _get_bgp_summary_json(switch):
    command = 'vtysh -c "show bgp summary json"'
    bgp_summary_json = '''
{
  "routerId":"1.1.1.1",
  "as":1,
  "vrfId":0,
  "vrfName":"Default",
  "tableVersion":3,
  "ribCount":5,
  "ribMemory":680,
  "peerCount":16,
  "peerMemory":344448,
  "peerGroupCount":1,
  "peerGroupMemory":72,
  "peers":{
    "fd35:1:1:2::1":{
      "hostname":"d1-p1-l2-r1",
      "remoteAs":1,
      "version":4,
      "msgRcvd":19,
      "msgSent":22,
      "tableVersion":0,
      "outq":0,
      "inq":0,
      "peerUptime":"00:03:28",
      "peerUptimeMsec":208000,
      "peerUptimeEstablishedEpoch":1498340876,
      "prefixReceivedCount":2,
      "state":"Established",
      "idType":"ipv6"
    },
    "fd35:1:1:2::2":{
      "remoteAs":0,
      "version":4,
      "msgRcvd":0,
      "msgSent":0,
      "tableVersion":0,
      "outq":0,
      "inq":0,
      "peerUptime":"never",
      "peerUptimeMsec":0,
      "prefixReceivedCount":0,
      "state":"Active",
      "idType":"ipv6"
    },
    "fd35:1:1:2::3":{
      "remoteAs":0,
      "version":4,
      "msgRcvd":0,
      "msgSent":0,
      "tableVersion":0,
      "outq":0,
      "inq":0,
      "peerUptime":"never",
      "peerUptimeMsec":0,
      "prefixReceivedCount":0,
      "state":"Active",
      "idType":"ipv6"
    }
  }
}
    '''
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
    input = {}
    
    for peer in bgp_neighbors_json:
        if peer == neighbor:
            input[neighbor] = bgp_neighbors_json[peer]
            
    print json.dumps(input, sort_keys=True, indent=4, separators=(',', ': '))
    

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