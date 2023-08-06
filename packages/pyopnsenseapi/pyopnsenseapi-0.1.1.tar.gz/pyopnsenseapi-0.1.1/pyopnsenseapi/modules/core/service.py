"""OPNsense core.service module."""

from pyopnsenseapi.modules.core.const import (ENDPOINTS)

SERVICE_RESTART = "service.restart?$name=%s&$id=%s"
SERVICE_SEARCH = "service.search"
SERVICE_START = "service.start?$name=%s&$id=%s"
SERVICE_STOP = "service.stop?$name=%s&$id=%s"


class Service(object):
    """OPNsense core.service module."""

    is_controller = True

    def __init__(self, client) -> None:
        self._client = client

    def restart(self,
                name: str,
                id: str = ""):
        """Restart a given service."""
        return self._client.post(
            endpoint=str(ENDPOINTS.get(SERVICE_RESTART)).format(name, id)
        )

    def start(self,
                name: str,
                id: str = ""):
        """Start a given service."""
        return self._client.post(
            endpoint=str(ENDPOINTS.get(SERVICE_START)).format(name, id)
        )

    def stop(self,
                name: str,
                id: str = ""):
        """Stops a given service."""
        return self._client.post(
            endpoint=str(ENDPOINTS.get(SERVICE_STOP)).format(name, id)
        )

    def search(self,
                      row_count: int = 500,
                      current_page: int = 1,
                      sort: str = "",
                      search_phrase: str = ""):
        """Search all services."""
        return self._client.post(
            endpoint=ENDPOINTS.get(SERVICE_SEARCH),
            body={
                "searchPhrase": search_phrase,
                "rowCount": row_count,
                "current": current_page,
                "sort": sort
            })
