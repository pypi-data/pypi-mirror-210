"""OPNsense diagnostics.netflow module."""

from pyopnsenseapi.modules.diagnostics.const import (ENDPOINTS)

NETFLOW_CACHE_STATS = "netflow.cacheStats"
NETFLOW_GET_CONFIG = "netflow.getconfig"
NETFLOW_IS_ENABLED = "netflow.isEnabled"
NETFLOW_RECONFIGURE = "netflow.reconfigure"
NETFLOW_SET_CONFIG = "netflow.setconfig"
NETFLOW_STATUS = "netflow.status"

class Netflow(object):
    """OPNsense diagnostics.netflow module."""

    is_controller = True

    def __init__(self, client) -> None:
        self._client = client

    def get_cache_stats(self):
        """Return netflow cache stats."""
        return self._client.get(ENDPOINTS.get(NETFLOW_CACHE_STATS))

    def get_config(self):
        """getConfig."""
        return self._client.get(ENDPOINTS.get(NETFLOW_GET_CONFIG))["netflow"]

    def is_enabled(self):
        """Return netflow enabled."""
        return self._client.get(ENDPOINTS.get(NETFLOW_IS_ENABLED))

    def reconfigure(self):
        """Reconfigure netflow."""
        return self._client.post(
            endpoint=ENDPOINTS.get(NETFLOW_RECONFIGURE),
            body={})

    def set_config(self, config):
        """Set netflow config."""
        return self._client.post(
            endpoint=ENDPOINTS.get(NETFLOW_SET_CONFIG),
            body={
                "netflow": config
            })

    def status(self):
        """Return netflow status."""
        return self._client.get(ENDPOINTS.get(NETFLOW_STATUS))
