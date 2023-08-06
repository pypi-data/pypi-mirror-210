"""OPNsense diagnostics.traffic module."""
# pylint: disable=consider-using-enumerate

from pyopnsenseapi.modules.diagnostics.const import (ENDPOINTS)

TRAFFIC_GET_INTERFACE = "traffic.Interface"
TRAFFIC_GET_TOP = "traffic.Top?$interfaces=%s"

class Traffic(object):
    """OPNsense diagnostics.systemhealth module."""

    is_controller = True

    def __init__(self, client) -> None:
        self._client = client

    def get_interfaces(self):
        """Return interface health status."""
        return self._client.get(ENDPOINTS.get(TRAFFIC_GET_INTERFACE))

    def top(self,
            interfaces: list):
        """Return RRD list."""
        ifaces = ""
        for i in range(len(interfaces)):
            ifaces = ifaces + interfaces[i]
            if i != len(interfaces)-1:
                ifaces = ifaces + ','

        return self._client.get(str(ENDPOINTS.get(TRAFFIC_GET_TOP)).format(ifaces))
