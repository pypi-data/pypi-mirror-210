"""OPNsense DNS diagnostics."""

from pyopnsenseapi.modules.diagnostics.const import (ENDPOINTS)

DNS_REVERSE_LOOKUP = "dns.reverseLookup"

class Dns(object):
    """OPNsense diagnostics.dns module."""

    is_controller = True

    def __init__(self, client) -> None:
        self._client = client

    def reverse_lookup(self, address: str):
        """Return current system activity."""
        return self._client.get(ENDPOINTS.get(DNS_REVERSE_LOOKUP).format(address), True)
