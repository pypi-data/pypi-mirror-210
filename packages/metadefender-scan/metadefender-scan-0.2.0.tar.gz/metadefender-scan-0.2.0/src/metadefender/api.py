import json
import os
import time
import urllib3
from typing import Union

import requests


class MetadefenderApi:
    def __init__(
        self,
        srv_address: str,
        verify_ssl: bool = True,
        json_decode: bool = False,
        rule: str = None,
    ) -> None:
        """Interface for requests to MetaDefender Core v4 API.
        This class was created to allow automated file scans without using MetaDefender web interface.

        Args:
            srv_address (str): URL of a MetaDefender server.
            verify_ssl (bool, optional): Enable SSL verification for HTTP requests. Defaults to True.
            json_decode (bool, optional): specifies if API JSON response should be converted to dict. Defaults to False.
            rule (str, optional): scanning rule to use. Defaults to None.
        """
        self.srv_address = srv_address.strip() if isinstance(srv_address, str) else None
        self.verify_ssl = verify_ssl
        self.json_decode = bool(json_decode)
        self.rule = rule

        self.headers_default = dict()

        if not self.verify_ssl:
            # Disable warning for non-SSL connections
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return

    def _request_api(
        self,
        request_url: str,
        headers: dict = None,
        body: bytes = None,
        method: str = "GET",
    ) -> str:
        """Send request to MetaDefender API.

        Args:
            request_url (str): full request URL.
            headers (dict, optional): HTTP headers. Defaults to None.
            body (bytes, optional): body of the request. Defaults to None.
            method (str, optional): request method. Defaults to "GET".

        Raises:
            ValueError: when HTTP method is invalid.
            MetadefenderApiException: when HTTP request to MetaDefender API failed.

        Returns:
            str: unprocessed MetaDefender API response.
        """
        if method == "GET":
            response = requests.get(request_url, headers=headers, verify=self.verify_ssl)
        elif method == "POST":
            response = requests.post(request_url, headers=headers, data=body, verify=self.verify_ssl)
        else:
            raise ValueError("Invalid HTTP method: {0}".format(method))

        try:
            response.raise_for_status()
        except requests.RequestException:
            raise MetadefenderApiException(
                "HTTP{0}: {1}".format(response.status_code, response.reason),
                response.status_code,
                response.reason,
                response.text,
            )
        else:
            return response.content

    def _decode_api_response(self, api_response: str) -> Union[str, dict]:
        """Decodes response from API to string or to dictionary.

        Args:
            api_response (str): unprocessed string with MetaDefender API response

        Returns:
            Union[str, dict]: MetaDefender API response
        """
        string = api_response.decode("utf-8")
        return json.loads(string) if self.json_decode else string

    def login(self, user: str, password: str) -> None:
        """Initiate a new session for user. Required for using protected REST APIs.

        Args:
            user (str): Username
            password (str): User's password
        """
        request_url = "/".join([self.srv_address, "login"])

        headers = dict()
        headers["user"] = user
        headers["password"] = password

        api_response = self._request_api(request_url, headers, method="POST")
        response_json = json.loads(api_response.decode("utf-8"))

        try:
            apikey = response_json["session_id"]
        except KeyError:
            raise MetadefenderApiException("Failed to login")
        else:
            self.headers_default["apikey"] = apikey

    def logout(self) -> None:
        """Destroy user's session."""
        if self.headers_default.get("apikey"):
            request_url = "/".join([self.srv_address, "logout"])
            headers = dict(self.headers_default)
            _ = self._request_api(request_url, headers, method="POST")

    def get_hash_details(self, hash_value: str) -> Union[str, dict]:
        """Get details of previously scanned file using file hash

        Arguments:
            hash_value {str} -- hash value of file (MD5, SHA1, SHA256)

        Returns:
            str -- API JSON response if class was created with parameter json_decode = True
            dict -- converted API JSON response if class was created with parameter json_decode = False
        """
        request_url = "/".join([self.srv_address, "hash", str(hash_value)])
        headers = dict(self.headers_default)
        api_reponse = self._request_api(request_url, headers, method="GET")
        return self._decode_api_response(api_reponse)

    def upload_file(self, filename: str, archivepwd: str = None) -> Union[str, dict]:
        """Upload a new file to MetaDefender service for scanning.

        Args:
            filename (str): Local path for file to be scanned.
            archivepwd (str, optional): Password for protected archive. Defaults to None.

        Returns:
            Union[str, dict]: MetaDefender API response
        """
        request_url = "/".join([self.srv_address, "file"])

        headers = dict(self.headers_default)
        headers["Content-Type"] = "application/octet-stream"
        headers["filename"] = os.path.basename(filename)

        if self.rule is not None:
            headers["rule"] = self.rule
        if archivepwd is not None:
            headers["archivepwd"] = archivepwd

        with open(filename, "rb") as fd:
            api_reponse = self._request_api(request_url, headers, fd, method="POST")

        return self._decode_api_response(api_reponse)

    def wait_for_scan(self, data_id: str, interval: int = 1) -> None:
        """Wait for job with specified data_id to be finished by server.
        Check status every X seconds specified in interval.

        Args:
            data_id (str): process identifier returned in JSON from upload_file function
            interval (int, optional): number of seconds between checks. Defaults to 1.
        """
        while json.loads(self.get_scan_result(data_id))["process_info"]["progress_percentage"] != 100:
            time.sleep(interval)

    def get_scan_result(self, data_id: str) -> Union[str, dict]:
        """Get scanning results from MetaDefender.

        Args:
            data_id (str): process identifier returned in JSON from upload_file function

        Returns:
            Union[str, dict]: MetaDefender API response
        """
        request_url = "/".join([self.srv_address, "file", str(data_id)])
        headers = dict(self.headers_default)
        api_reponse = self._request_api(request_url, headers, method="GET")
        return self._decode_api_response(api_reponse)

    def download_sanitized_file(self, data_id: str, filename: str) -> None:
        """Download sanitized file from MetaDefender.
        This will fail of file was scanned with private processing enabled.

        Args:
            data_id (str): process identifier returned in JSON from upload_file function
            filename (str): path to save sanitized file on local system
        """
        request_url = "/".join([self.srv_address, "file", "converted", str(data_id)])
        headers = dict(self.headers_default)
        api_reponse = self._request_api(request_url, headers, method="GET")

        with open(filename, "wb") as fd:
            fd.write(api_reponse)


class MetadefenderApiException(Exception):
    def __init__(self, message, status_code, reason, text):
        super(MetadefenderApiException, self).__init__(message)

        self.status_code = status_code
        self.reason = reason
        self.text = text
