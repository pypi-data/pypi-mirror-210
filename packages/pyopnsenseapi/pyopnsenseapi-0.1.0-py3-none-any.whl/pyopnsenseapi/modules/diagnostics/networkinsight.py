"""OPNsense diagnostics.networkinsight module."""

from pyopnsenseapi.modules.diagnostics.const import (ENDPOINTS)

NETWORKINSIGHT_GET_INTERFACES = "networkinsight.getInterfaces"
NETWORKINSIGHT_GET_METADATA = "networkinsight.getMetadata"
NETWORKINSIGHT_GET_PROTOCOLS = "networkinsight.getProtocols"
NETWORKINSIGHT_GET_SERVICES = "networkinsight.getServices"

class NetworkInsight(object):
    """OPNsense diagnostics.networkinsight module."""

    is_controller = True

    def __init__(self, client) -> None:
        self._client = client

    def get_interfaces(self):
        """Return network interfaces."""
        return self._client.get(ENDPOINTS.get(NETWORKINSIGHT_GET_INTERFACES))

    def get_metadata(self):
        """Return metadata."""
        return self._client.get(ENDPOINTS.get(NETWORKINSIGHT_GET_METADATA))

    def get_protocols(self):
        """Return protocols."""
        return self._client.get(ENDPOINTS.get(NETWORKINSIGHT_GET_PROTOCOLS))

    def get_services(self):
        """Return services."""
        return self._client.get(ENDPOINTS.get(NETWORKINSIGHT_GET_SERVICES))
