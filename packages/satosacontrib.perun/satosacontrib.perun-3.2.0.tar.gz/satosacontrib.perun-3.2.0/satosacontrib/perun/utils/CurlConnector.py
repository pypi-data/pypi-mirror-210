import http.cookiejar
from typing import Union, Optional, List

import collections
import urllib.parse
import time

from json import dumps, loads

import requests
import requests.cookies

from satosacontrib.perun.utils.CurlConnectorInterface import CurlInterface
from perun.connector import Logger


class CurlConnector(CurlInterface):
    """This is a class for curl connector.

    Options for curl object are set by default
    but you can override them -> see CurlConnectorInterface
    """

    _CONNECT_TIMEOUT = 1

    _TIMEOUT = 15

    def __init__(
        self,
        url: str,
        params: dict[str, Union[str, Optional[int], bool, List[str], dict[str, str]]],
        cookie_file: str = "/tmp/proxyidp_cookie.txt",
    ):
        if not params:
            params = {}
        self.url = url
        self.params = params
        self._logger = Logger.get_logger(self.__class__.__name__)
        self._session = requests.Session()
        self._cookie_file = cookie_file
        self._jar = http.cookiejar.LWPCookieJar(filename=self._cookie_file)
        try:
            self._jar.load()
        except (FileNotFoundError, http.cookiejar.LoadError):
            self._jar.save()
        self._session.cookies = self._jar
        self._auth = ("", "")
        self._connect_timeout = self._CONNECT_TIMEOUT
        self._timeout = self._TIMEOUT

    def setopt_userpwd(self, user, password):
        self._auth = (user, password)

    def setopt_connecttimeout(self, connect_timeout):
        self._connect_timeout = connect_timeout

    def setopt_timeout(self, timeout):
        self._timeout = timeout

    def get(self):
        params_query = self._http_build_query(self.params)
        start_time = time.time()
        response = self._session.get(
            self.url + "?" + params_query,
            auth=self._auth,
            timeout=(self._connect_timeout, self._timeout),
        )
        end_time = time.time()
        response_time = round(end_time - start_time, 3)
        self._logger.debug(
            "requests: GET call",
            self.url,
            "with params:",
            params_query,
            "response :",
            response.text,
            "in",
            str(response_time) + "s.",
        )
        self._jar.save()
        return self._load_response("GET", params_query, response.text)

    def post(self):
        params_json = dumps(self.params)
        start_time = time.time()
        headers = {
            "Content-Type": "application/json",
            "Content-Length": str(len(params_json)),
        }
        response = self._session.post(
            self.url,
            headers=headers,
            json=params_json,
            auth=self._auth,
            timeout=(self._connect_timeout, self._timeout),
        )
        end_time = time.time()
        response_time = round(end_time - start_time, 3)
        self._logger.debug(
            "curl: POST call",
            self.url,
            "with params:",
            params_json,
            "response :",
            response.text,
            "in",
            str(response_time) + "s.",
        )
        self._jar.save()
        return self._load_response("POST", params_json, response.text)

    def _load_response(self, request_type, params, json):
        if not json:
            raise Exception(
                "Cant't get response from Url. Call: "
                + self.url
                + ", Params: "
                + params
                + ", Response: "
                + json
            )
        try:
            result = loads(json)
            return result
        except ValueError:
            self._logger.warning(
                f"curl: {request_type} call failed. Call: "
                + self.url
                + ", Params: "
                + params
                + ", Response: "
                + json
            )

    @staticmethod
    def _http_build_query(data):
        dct = collections.OrderedDict()
        for key, value in data.items():
            if isinstance(value, list):
                for index, element in enumerate(value):
                    dct["{0}[{1}]".format(key, index)] = element
            else:
                dct[key] = str(value)
        return urllib.parse.urlencode(dct)
