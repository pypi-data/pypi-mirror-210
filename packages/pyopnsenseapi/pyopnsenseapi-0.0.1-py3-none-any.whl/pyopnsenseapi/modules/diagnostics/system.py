"""OPNsense diagnostics.system module."""

from pyopnsenseapi.modules.diagnostics.const import (ENDPOINTS)

SYSTEM_MEMORY = "system.memory"

class System(object):
    """OPNsense diagnostics.system module."""

    is_controller = True

    def __init__(self, client) -> None:
        self._client = client

    def get_memory(self):
        """Return current system memory."""
        return self._client.get(ENDPOINTS.get(SYSTEM_MEMORY))
