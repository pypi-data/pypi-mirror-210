"""OPNsense diagnostics.firewall module."""

from pyopnsenseapi.modules.diagnostics.const import (ENDPOINTS)

FIREWALL_DEL_STATE = "firewall.delState"
FIREWALL_FLUSH_SOURCES = "firewall.flushSources"
FIREWALL_FLUSH_STATES = "firewall.flushStates"
FIREWALL_KILL_STATES = "firewall.killStates"
FIREWALL_LIST_RULE_IDS = "firewall.listRuleIds"
FIREWALL_LOG = "firewall.log"
FIREWALL_LOG_FILTERS = "firewall.logFilters"
FIREWALL_PF_STATS = "firewall.pfStatistics?$section=%s"
FIREWALL_Q_PF_TOP = "firewall.queryPfTop"
FIREWALL_Q_STATES = "firewall.queryStates"
FIREWALL_STATS = "firewall.stats"

class Firewall(object):
    """OPNsense diagnostics.firewall module."""

    is_controller = True

    def __init__(self, client) -> None:
        self._client = client

    
    def delete_state(self, stateid: str, creatorid: str):
        """Deletes a given state."""
        return self._client.post(
            endpoint=ENDPOINTS.get(FIREWALL_DEL_STATE),
            body={"stateid": stateid, "creatorid": creatorid}
        )

    
    def flush_sources(self):
        """Flushes sources."""
        return self._client.post(
            endpoint=ENDPOINTS.get(FIREWALL_FLUSH_SOURCES),
            body={}
        )

    
    def flush_states(self):
        """Flushes states."""
        return self._client.post(
            endpoint=ENDPOINTS.get(FIREWALL_FLUSH_STATES),
            body={}
        )

    
    def kill_states(self):
        """Kills states."""
        return self._client.post(
            endpoint=ENDPOINTS.get(FIREWALL_KILL_STATES),
            body={}
        )

    
    def get_rule_ids(self):
        """Gets a list of rule IDs."""
        return self._client.get(ENDPOINTS.get(FIREWALL_LIST_RULE_IDS))

    
    def get_firewall_log(self):
        """Returns the firewall log."""
        return self._client.get(ENDPOINTS.get(FIREWALL_LOG))

    
    def get_firewall_log_filters(self):
        """Returns firewall log filters?."""
        return self._client.get(ENDPOINTS.get(FIREWALL_LOG_FILTERS))

    
    def get_pf_statistics(self, section: str="null"):
        """Returns pfStatistics."""
        return self._client.get(str(ENDPOINTS.get(FIREWALL_PF_STATS)).format(section))

    
    def search_pf_top(self,
                      row_count: int = 500,
                      current_page: int = 1,
                      rule_id: str = "",
                      sort: str = "",
                      search_phrase: str = ""):
        """Returns pfTop."""
        return self._client.post(
            endpoint=ENDPOINTS.get(FIREWALL_Q_PF_TOP),
            body={
                "searchPhrase": search_phrase,
                "rowCount": row_count,
                "current": current_page,
                "ruleid": rule_id,
                "sort": sort
            })

    
    def search_states(self,
                      row_count: int = 500,
                      current_page: int = 1,
                      rule_id: str = "",
                      sort: str = "",
                      search_phrase: str = ""):
        """Returns pfTop."""
        return self._client.post(
            endpoint=ENDPOINTS.get(FIREWALL_Q_STATES),
            body={
                "searchPhrase": search_phrase,
                "rowCount": row_count,
                "current": current_page,
                "ruleid": rule_id,
                "sort": sort
            })

    
    def get_statistics(self):
        """Returns statistics."""
        return self._client.get(ENDPOINTS.get(FIREWALL_STATS))
