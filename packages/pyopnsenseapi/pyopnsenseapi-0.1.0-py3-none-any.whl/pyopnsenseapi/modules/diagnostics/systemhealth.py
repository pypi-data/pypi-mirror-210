"""OPNsense diagnostics.systemhealth module."""

from pyopnsenseapi.modules.diagnostics.const import (ENDPOINTS)

SYSTEM_HEALTH_GET_INTERFACES = "systemhealth.getInterfaces"
SYSTEM_HEALTH_GET_RRD_LIST = "systemhealth.getRRDlist"

class SystemHealth(object):
    """OPNsense diagnostics.systemhealth module."""

    is_controller = True

    def __init__(self, client) -> None:
        self._client = client

    def get_interfaces(self):
        """Return interface health status."""
        return self._client.get(ENDPOINTS.get(SYSTEM_HEALTH_GET_INTERFACES))

    def get_rrd_list(self):
        """Return RRD list."""
        return self._client.get(ENDPOINTS.get(SYSTEM_HEALTH_GET_RRD_LIST))
