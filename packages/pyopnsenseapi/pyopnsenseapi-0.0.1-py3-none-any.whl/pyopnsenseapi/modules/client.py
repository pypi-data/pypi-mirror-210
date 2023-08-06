"""OPNsense client."""

import json
import requests
import urllib3
from pyopnsenseapi.const import (DEFAULT_TIMEOUT, HTTP_SUCCESS)
from pyopnsenseapi.modules import Modules

class Client(object):
    """The root client object."""

    is_module = False

    def __init__(self, api_key: str,
                 api_secret: str,
                 host: str,
                 use_ssl: bool,
                 verify_cert: bool=False,
                 timeout: int=DEFAULT_TIMEOUT) -> None:
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = host + "/api/"
        self.use_ssl = use_ssl
        self.verify_cert = verify_cert
        self.timeout = timeout

        if self.use_ssl:
            self.base_url = "https://" + self.base_url
        else:
            self.base_url = "http://" + self.base_url

        if not verify_cert:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        self.modules = Modules(self)

    def _process_response(self, response, raw=False):
        """Handle the response."""
        if response.status_code in HTTP_SUCCESS:
            return response.text if raw else json.loads(response.text)
        else:
            raise Exception(
                status_code=response.status_code, resp_body=response.text)

    def get(self, endpoint: str, raw=False):
        """Send a get request to the OPNsense API."""
        req_url = self.base_url + endpoint
        response = requests.get(req_url, verify=self.verify_cert,
                                auth=(self.api_key, self.api_secret),
                                timeout=self.timeout)
        return self._process_response(response, raw)

    def post(self, endpoint: str, body, raw=False):
        """Send a post request to the OPNsense API."""
        req_url = self.base_url + endpoint
        response = requests.post(req_url, data=body, verify=self.verify_cert,
                                 auth=(self.api_key, self.api_secret),
                                 timeout=self.timeout)
        return self._process_response(response, raw)
