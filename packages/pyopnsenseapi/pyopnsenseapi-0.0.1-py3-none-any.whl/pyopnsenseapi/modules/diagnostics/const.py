"""OPNsense diagnostics module endpoints."""

DIAGNOSTICS = "diagnostics"

FUNCTIONS = {
    "ACTIVITY_GET_ACTIVITY": "activity.getActivity",
    "DNS_REVERSE_LOOKUP": "dns.reverseLookup?address=%s",
    "DNS_DIAGNOSTICS_GET": "dns_diagnostics.get",
    "DNS_DIAGNOSTICS_SET": "dns_diagnostics.set",
    "FIREWALL_DEL_STATE": "firewall.delState",
    "FIREWALL_FLUSH_SOURCES": "firewall.flushSources",
    "FIREWALL_FLUSH_STATES": "firewall.flushStates",
    "FIREWALL_KILL_STATES": "firewall.killStates",
    "FIREWALL_LIST_RULE_IDS": "firewall.listRuleIds",
    "FIREWALL_LOG": "firewall.log",
    "FIREWALL_LOG_FILTERS": "firewall.logFilters",
    "FIREWALL_PF_STATS": "firewall.pfStatistics?$section=%s",
    "FIREWALL_Q_PF_TOP": "firewall.queryPfTop",
    "FIREWALL_Q_STATES": "firewall.queryStates",
    "FIREWALL_STATS": "firewall.stats",
    "INTERFACE_CARP_STATUS": "interface.CarpStatus?$status=%s",
    "INTERFACE_DEL_ROUTE": "interface.delRoute",
    "INTERFACE_FLUSH_ARP": "interface.flushArp",
    "INTERFACE_GET_ARP": "interface.getArp",
    "INTERFACE_GET_BPF_STATS": "interface.getBpfStatistics",
    "INTERFACE_GET_CONFIG": "interface.getInterfaceConfig",
    "INTERFACE_GET_NAMES": "interface.getInterfaceNames",
    "INTERFACE_GET_STATS": "interface.getInterfaceStatistics",
    "INTERFACE_GET_MEM_STATS": "interface.getMemoryStatistics",
    "INTERFACE_GET_NDP": "interface.getNdp",
    "INTERFACE_GET_NETISR_STATS": "interface.getNetisrStatistics",
    "INTERFACE_GET_PFSYNC_NODES": "interface.getPfSyncNodes",
    "INTERFACE_GET_PROTO_STATS": "interface.getProtocolStatistics",
    "INTERFACE_GET_ROUTES": "interface.getRoutes",
    "INTERFACE_GET_SOCKET_STATS": "interface.getSocketStatistics",
    "INTERFACE_GET_VIP_STATUS": "interface.getVipStatus",
    "INTERFACE_SEARCH_ARP": "interface.searchArp",
    "INTERFACE_SEARCH_NDP": "interface.searchNdp",
    "NETFLOW_CACHE_STATS": "netflow.cacheStats",
    "NETFLOW_GET_CONFIG": "netflow.getconfig",
    "NETFLOW_IS_ENABLED": "netflow.isEnabled",
    "NETFLOW_RECONFIGURE": "netflow.reconfigure",
    "NETFLOW_SET_CONFIG": "netflow.setconfig",
    "NETFLOW_STATUS": "netflow.status",
    "NETWORKINSIGHT_GET_INTERFACES": "networkinsight.getInterfaces",
    "NETWORKINSIGHT_GET_METADATA": "networkinsight.getMetadata",
    "NETWORKINSIGHT_GET_PROTOCOLS": "networkinsight.getProtocols",
    "NETWORKINSIGHT_GET_SERVICES": "networkinsight.getServices",
    "PACKET_CAPTURE_DOWNLOAD": "packet_capture.download?$jobid=%s",
    "PACKET_CAPTURE_GET": "packet_capture.get",
    "PACKET_CAPTURE_MACINFO": "packet_capture.macInfo?$macAddr=%s",
    "PACKET_CAPTURE_REMOVE": "packet_capture.remove?$jobid=%s",
    "PACKET_CAPTURE_SEARCHJOBS": "packet_capture.searchJobs",
    "PACKET_CAPTURE_SET": "packet_capture.set",
    "PACKET_CAPTURE_START": "packet_capture.start?$jobid=%s",
    "PACKET_CAPTURE_STOP": "packet_capture.stop?$jobid=%s",
    "PACKET_CAPTURE_VIEW": "packet_capture.view?$jobid=%s&$detail=%s",
    "SYSTEM_MEMORY": "system.memory",
    "SYSTEM_HEALTH_GET_INTERFACES": "systemhealth.getInterfaces",
    "SYSTEM_HEALTH_GET_RRD_LIST": "systemhealth.getRRDlist",
    "TRAFFIC_INTERFACE_GET": "traffic.Interface",
    "TRAFFIC_TOP_GET": "traffic.Top",
}

# Dynamic build endpoints
ENDPOINTS = {}
for v in FUNCTIONS.items():
    ENDPOINTS[str(v[1])] = f"{DIAGNOSTICS}/{str(v[1]).replace('.', '/')}"
