#!/usr/bin/python

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
'''

BGP_NEIGHBOR_NOT_ESTABLISHED_TEMPLATE = '''
Neighbor {} with remote AS {}
  Current State is {}
  BGP version is {}, {}'s Router ID is {}
  Hold time is {}, keepalive time is {}
  Message advertisement runs is {}
  Connect retry timer is {}
'''

def get_bgp_neighbor_established(bgp_neighbors_json, peer):
    return BGP_NEIGHBOR_ESTABLISHED_TEMPLATE.format(
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
        bgp_neighbors_json[peer]["nexthop"], bgp_neighbors_json[peer]["nexthopGlobal"], bgp_neighbors_json[peer]["nexthopLocal"]
    )


def get_bgp_neighbor_not_established(bgp_neighbors_json, peer):
    return BGP_NEIGHBOR_NOT_ESTABLISHED_TEMPLATE.format(
        peer, bgp_neighbors_json[peer]["remoteAs"],
        bgp_neighbors_json[peer]["bgpState"],
        bgp_neighbors_json[peer]["bgpVersion"],
        peer, bgp_neighbors_json[peer]["remoteRouterId"],
        int(bgp_neighbors_json[peer]["bgpTimerHoldTimeMsecs"]) / 1000,
        int(bgp_neighbors_json[peer]["bgpTimerKeepAliveIntervalMsecs"]) / 1000,
        int(bgp_neighbors_json[peer]["minBtwnAdvertisementRunsTimerMsecs"]) / 1000,
        bgp_neighbors_json[peer]["connectRetryTimer"]
    )
    