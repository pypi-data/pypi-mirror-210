"""OPNsense diagnostics.activity module."""

from pyopnsenseapi.modules.diagnostics.const import (ENDPOINTS)
#from pyopnsenseapi.modules.diagnostics import Diagnostics

ACTIVITY_GET_ACTIVITY = "activity.getActivity"

class Activity(object):
    """OPNsense diagnostics.activity module."""

    is_controller = True

    def __init__(self, client) -> None:
        self._client = client

    def get(self):
        """Return current system activity."""
        return self._client.get(ENDPOINTS.get(ACTIVITY_GET_ACTIVITY))
