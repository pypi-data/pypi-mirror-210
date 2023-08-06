import requests
import json
from enum import Enum
from turandot import TurandotConnectionException
from turandot.model import ConfigDict


class ZoteroDataFormat(Enum):
    BIBTEX = "biblatex"
    CSLJSON = "json"


class ZoteroConnector:
    """Connect to Zoteros BetterBibtex extension to get bibliographic data"""

    def __init__(self, config: ConfigDict):
        self.hostname = config.get_key(['api', 'zotero', 'host'], "localhost")
        self.port = config.get_key(['api', 'zotero', 'port'], 23119)
        self.connection_error = TurandotConnectionException(
            "No answer from {}:{}. Zotero and/or Better Bibtex extension not running?".format(self.hostname, self.port)
        )

    def _assemble_url(self, endpoint):
        """Assemble endpoint specific url"""
        return "http://{}:{}{}".format(self.hostname, self.port, endpoint)

    def get_libraries(self) -> list:
        """
        Get list of zotero libs with their IDs
        ct. https://github.com/retorquere/zotero-better-bibtex/issues/787
        :return: List of Zotero Libraries
        """
        endpoint = "/better-bibtex/json-rpc"
        payload = json.dumps({"jsonrpc": "2.0", "method": "user.groups"})
        headers = {'content-type': 'application/json'}
        url = self._assemble_url(endpoint)
        try:
            response = requests.post(url, data=payload, headers=headers)
            if response.status_code == 404:
                raise self.connection_error
            libs = json.loads(response.content.decode())
            return libs["result"]
        except requests.exceptions.ConnectionError:
            raise self.connection_error

    def get_bib_data(self, libid: int, form: ZoteroDataFormat) -> str:
        """
        Get bibliographic data from Zotero
        :param libid: Library to get data from
        :param form: Format: JSON or Bibtex
        :return: Bibliographic data in text format
        """
        endpoint = "/better-bibtex/export/library?/{}/library.{}".format(libid, form.value)
        url = self._assemble_url(endpoint)
        try:
            response = requests.get(url)
            return response.content.decode()
        except requests.exceptions.ConnectionError:
            raise self.connection_error

    def get_csljson(self, libid: int) -> str:
        """Get CSLJSON string from Zotero"""
        return self.get_bib_data(libid=libid, form=ZoteroDataFormat.CSLJSON)
