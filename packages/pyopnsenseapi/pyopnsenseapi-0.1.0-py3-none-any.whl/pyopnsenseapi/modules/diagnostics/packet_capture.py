"""OPNsense diagnostics.packet_capture module."""

from pyopnsenseapi.modules.diagnostics.const import (ENDPOINTS)
from pyopnsenseapi.modules.enums import (TracerDetail, IpAddressTypes)

PACKET_CAPTURE_DOWNLOAD = "packet_capture.download?$jobid=%s"
PACKET_CAPTURE_GET = "packet_capture.get"
PACKET_CAPTURE_MACINFO = "packet_capture.macInfo?$macAddr=%s"
PACKET_CAPTURE_REMOVE = "packet_capture.remove?$jobid=%s"
PACKET_CAPTURE_SEARCHJOBS = "packet_capture.searchJobs"
PACKET_CAPTURE_SET = "packet_capture.set"
PACKET_CAPTURE_START = "packet_capture.start?$jobid=%s"
PACKET_CAPTURE_STOP = "packet_capture.stop?$jobid=%s"
PACKET_CAPTURE_VIEW = "packet_capture.view?$jobid=%s&$detail=%s"

class PacketCapture(object):
    """OPNsense diagnostics.packet_capture module."""

    is_controller = True

    def __init__(self, client) -> None:
        self._client = client

    def download(self, job_id: str):
        """Download a packet capture"""
        return self._client.get(
            endpoint=str(ENDPOINTS.get(PACKET_CAPTURE_DOWNLOAD)).format(job_id)
        )

    def get(self):
        """Get packet captures"""
        return self._client.get(
            endpoint=str(ENDPOINTS.get(PACKET_CAPTURE_GET))
        )

    def mac_info(self, mac_address):
        """Get MAC address info"""
        return self._client.get(
            endpoint=str(ENDPOINTS.get(PACKET_CAPTURE_MACINFO)).format(mac_address)
        )

    def remove(self, job_id: str):
        """Removes a packet capture job"""
        return self._client.post(
            endpoint=str(ENDPOINTS.get(PACKET_CAPTURE_REMOVE)).format(job_id)
        )

    def search(self,
                      row_count: int = 500,
                      current_page: int = 1,
                      sort: str = "",
                      search_phrase: str = ""):
        """Search all packet capture jobs."""
        return self._client.post(
            endpoint=ENDPOINTS.get(PACKET_CAPTURE_SEARCHJOBS),
            body={
                "searchPhrase": search_phrase,
                "rowCount": row_count,
                "current": current_page,
                "sort": sort
            })

    def start(self,
              job_id: str):
        """Starts a packet capture job."""
        return self._client.post(
            endpoint=str(ENDPOINTS.get(PACKET_CAPTURE_START)).format(job_id),
            body={}
        )

    def stop(self,
              job_id: str):
        """Stops a packet capture job."""
        return self._client.post(
            endpoint=str(ENDPOINTS.get(PACKET_CAPTURE_STOP)).format(job_id),
            body={}
        )

    def view(self,
              job_id: str,
              detail: TracerDetail = TracerDetail.NORMAL):
        """Starts a packet capture job."""
        return self._client.get(
            endpoint=str(ENDPOINTS.get(PACKET_CAPTURE_START)).format(job_id, str(detail))
        )

    def create(self,
               interface: str,
               host: str = "",
               description: str = "",
               promiscuous: bool = False,
               ip_family: IpAddressTypes = IpAddressTypes.ANY,
               protocol_not: bool = False,
               protocol: str = "any",
               port_not: bool = False,
               port: int = -1,
               snaplen: int = -1,
               count: int = 100):
        """Creates a packet tracer job."""
        body={
            "interface": interface,
            "host": host,
            "description": description,
            "promiscuous": promiscuous,
            "fam": str(ip_family),
            "protocol_not": protocol_not,
            "protocol": protocol,
            "count": count
        }

        if port != -1:
            body["port"] = port
            body["port_not"] = port_not

        if snaplen != -1:
            body["snaplen"] = snaplen

        return self._client.post(
            endpoint=ENDPOINTS.get(PACKET_CAPTURE_SET),
            body=body
        )
