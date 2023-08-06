"""OPNsense diagnostics.dns_diagnostics module."""

from pyopnsenseapi.modules.diagnostics.const import (ENDPOINTS)

DNS_DIAGNOSTICS_GET = "dns_diagnostics.get"
DNS_DIAGNOSTICS_SET = "dns_diagnostics.set"

class DnsDiagnostics(object):
    """OPNsense diagnostics.dns_diagnostics module."""

    is_controller = True

    def __init__(self, client) -> None:
        self._client = client

    def get(self):
        """Unsure what this is currently."""
        return self._client.get(ENDPOINTS.get(DNS_DIAGNOSTICS_GET))

    def set(self):
        """Unsure what this is currently."""
        return self._client.get(ENDPOINTS.get(DNS_DIAGNOSTICS_SET))
