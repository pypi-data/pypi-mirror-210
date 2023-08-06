"""OPNsense diagnostics.interface module."""

from pyopnsenseapi.modules.diagnostics.const import (ENDPOINTS)
from pyopnsenseapi.modules.enums import (CarpStatus)

INTERFACE_CARP_STATUS = "interface.CarpStatus?$status=%s"
INTERFACE_DEL_ROUTE = "interface.delRoute"
INTERFACE_FLUSH_ARP = "interface.flushArp"
INTERFACE_GET_ARP = "interface.getArp"
INTERFACE_GET_BPF_STATS = "interface.getBpfStatistics"
INTERFACE_GET_CONFIG = "interface.getInterfaceConfig"
INTERFACE_GET_NAMES = "interface.getInterfaceNames"
INTERFACE_GET_STATS = "interface.getInterfaceStatistics"
INTERFACE_GET_MEM_STATS = "interface.getMemoryStatistics"
INTERFACE_GET_NDP = "interface.getNdp"
INTERFACE_GET_NETISR_STATS = "interface.getNetisrStatistics"
INTERFACE_GET_PFSYNC_NODES = "interface.getPfSyncNodes"
INTERFACE_GET_PROTO_STATS = "interface.getProtocolStatistics"
INTERFACE_GET_ROUTES = "interface.getRoutes"
INTERFACE_GET_SOCKET_STATS = "interface.getSocketStatistics"
INTERFACE_GET_VIP_STATUS = "interface.getVipStatus"
INTERFACE_SEARCH_ARP = "interface.searchArp"
INTERFACE_SEARCH_NDP = "interface.searchNdp"

class Interface(object):
    """OPNsense diagnostics.interface module."""

    is_controller = True

    def __init__(self, client) -> None:
        self._client = client

    def set_carp_status(self, status: CarpStatus):
        """Set new carp node status."""
        return self._client.post(
            endpoint=str(ENDPOINTS.get(INTERFACE_CARP_STATUS)).format(str(status))
        )

    def del_route(self, destination: str, gateway: str):
        """Deletes a route."""
        return self._client.post(
            endpoint=ENDPOINTS.get(INTERFACE_DEL_ROUTE),
            body={
                "destination": destination,
                "gateway": gateway
            }
        )

    def flush_arp(self):
        """Flush system arp cache."""
        return self._client.post(
            endpoint=ENDPOINTS.get(INTERFACE_FLUSH_ARP),
            body={}
        )


    def get_arp(self):
        """Get ARP table."""
        return self._client.get(
            endpoint=ENDPOINTS.get(INTERFACE_GET_ARP)
        )


    def get_bpf_statistics(self):
        """Get BPF statistics."""
        return self._client.get(
            endpoint=ENDPOINTS.get(INTERFACE_GET_BPF_STATS)
        )


    def get_config(self):
        """Get interface config."""
        return self._client.get(
            endpoint=ENDPOINTS.get(INTERFACE_GET_CONFIG)
        )


    def get_interface_names(self):
        """Get interface name(s)."""
        return self._client.get(
            endpoint=ENDPOINTS.get(INTERFACE_GET_NAMES)
        )


    def get_statistics(self):
        """Get interface stats."""
        return self._client.get(
            endpoint=ENDPOINTS.get(INTERFACE_GET_STATS)
        )


    def get_memory_statistics(self):
        """Get interface memory stats."""
        return self._client.get(
            endpoint=ENDPOINTS.get(INTERFACE_GET_MEM_STATS)
        )


    def get_ndp(self):
        """Get NDP table."""
        return self._client.get(
            endpoint=ENDPOINTS.get(INTERFACE_GET_NDP)
        )


    def get_netisr_statistics(self):
        """Get netisr statistics."""
        return self._client.get(
            endpoint=ENDPOINTS.get(INTERFACE_GET_NETISR_STATS)
        )


    def get_pfsync_nodes(self):
        """Get PFSync nodes."""
        return self._client.get(
            endpoint=ENDPOINTS.get(INTERFACE_GET_PFSYNC_NODES)
        )


    def get_protocol_statistics(self):
        """Get interface protocol stats."""
        return self._client.get(
            endpoint=ENDPOINTS.get(INTERFACE_GET_PROTO_STATS)
        )


    def get_routes(self):
        """Get routes."""
        return self._client.get(
            endpoint=ENDPOINTS.get(INTERFACE_GET_ROUTES)
        )


    def get_socket_statistics(self):
        """Get interface socket stats."""
        return self._client.get(
            endpoint=ENDPOINTS.get(INTERFACE_GET_SOCKET_STATS)
        )


    def get_vip_status(self):
        """Get VIP status."""
        return self._client.get(
            endpoint=ENDPOINTS.get(INTERFACE_GET_VIP_STATUS)
        )


    def search_arp_table(self,
                      row_count: int = 500,
                      current_page: int = 1,
                      rule_id: str = "",
                      sort: str = "",
                      search_phrase: str = ""):
        """Returns pfTop."""
        return self._client.post(
            endpoint=ENDPOINTS.get(INTERFACE_SEARCH_ARP),
            body={
                "searchPhrase": search_phrase,
                "rowCount": row_count,
                "current": current_page,
                "ruleid": rule_id,
                "sort": sort
            })


    def search_ndp_table(self,
                      row_count: int = 500,
                      current_page: int = 1,
                      rule_id: str = "",
                      sort: str = "",
                      search_phrase: str = ""):
        """Returns pfTop."""
        return self._client.post(
            endpoint=ENDPOINTS.get(INTERFACE_SEARCH_NDP),
            body={
                "searchPhrase": search_phrase,
                "rowCount": row_count,
                "current": current_page,
                "ruleid": rule_id,
                "sort": sort
            })
