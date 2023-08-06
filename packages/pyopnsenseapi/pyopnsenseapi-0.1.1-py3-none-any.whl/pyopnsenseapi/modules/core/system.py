"""OPNsense core.system module."""

from pyopnsenseapi.modules.core.const import (ENDPOINTS)

SYSTEM_DISMISS_STATUS = "system.dismissStatus"
SYSTEM_HALT = "system.halt"
SYSTEM_REBOOT = "system.reboot"
SYSTEM_STATUS = "system.status"

class System(object):
    """OPNsense core.service module."""

    is_controller = True

    def __init__(self, client) -> None:
        self._client = client

    def dismiss_status(self,
                       subject: str):
        """Dismisses a status by its subject"""
        return self._client.post(
            endpoint=ENDPOINTS.get(SYSTEM_DISMISS_STATUS),
            body={
                "subject": subject
            }
        )

    def reboot(self):
        """Reboot the OPNsense system."""
        return self._client.get(
            endpoint=ENDPOINTS.get(SYSTEM_REBOOT)
        )

    def shutdown(self):
        """Shutdown the OPNsense system."""
        return self._client.get(
            endpoint=ENDPOINTS.get(SYSTEM_HALT)
        )

    def status(self):
        """Gets the status of the OPNsense system."""
        return self._client.get(
            endpoint=ENDPOINTS.get(SYSTEM_STATUS)
        )
