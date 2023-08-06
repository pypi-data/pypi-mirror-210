import requests
import requests.packages
from json import JSONDecodeError
import logging
from typing import List, Dict
from .exceptions import BkwException

class Result:
    http_status_code: int
    http_message: str
    bkw_response: Dict
    bkw_status_code: int
    bkw_message: str


    def __init__(self, http_status_code: int, http_message: str = '', bkw_response: Dict = {}):
        """A wrapper for the BankruptcyWatch request response.

        Args:
            status_code (int): The HTTP status code response.
            message (str, optional): The HTTP response message. Defaults to ''.
            data (List[Dict], optional): The HTTP response data. Defaults to None.
        """
        self.http_status_code = int(http_status_code)
        self.http_message = str(http_message)
        self.bkw_response = bkw_response if bkw_response else {}
        self.bkw_status_code = int(self.bkw_response['status']) if self.bkw_response and 'status' in self.bkw_response else -1
        self.bkw_message = str(self.bkw_response['message']) if self.bkw_response and 'message' in self.bkw_response else ''


class RestAdapter:
    def __init__(self, hostname: str = 'api.bk.watch/api', ver: str = '2022-08-01', username: str = "", password: str = "", ssl_verify: bool = True, logger: logging.Logger = None):
        """Constructor for RestAdapter

        Args:
            hostname (str, optional): The BankruptcyWatch host. Defaults to 'api.bk.watch/api'.
            ver (str, optional): The BankruptcyWatch version. Defaults to '2021-11-01'.
            username (str, optional): The username for the BankruptcyWatch API account. Defaults to "".
            password (str, optional): The password for the BankruptcyWatch API account. Defaults to "".
            ssl_verify (bool, optional): SSL/TLS cert validation. If having SSL/TLS cert validation issues, can turn off with False. Defaults to True.
            logger (logging.Logger, optional): Python logging. Defaults to None.
        """
        self._logger = logger or logging.getLogger(__name__)
        self.url = "https://{}/{}".format(hostname, ver)
        self.username = username
        self.password = password
        self._ssl_verify = ssl_verify
        if not ssl_verify:
            # noinspection PyUnresolvedReferences
            requests.packages.urllib3.disable_warnings()
    
    def _do(self, http_method: str, operation: str, ep_params: Dict = {}, data: Dict = None) -> Result:
        """Runs the BankruptcyWatch HTTP request in the specified HTTP method.

        Args:
            http_method (str): The HTTP method e.g. 'GET'
            operation (str): The BankruptcyWatch operation e.g. ListDistricts
            ep_params (Dict, optional): The BankruptcyWatch parameters. Defaults to {}.
            data (Dict, optional): The data included for a PUT request. Defaults to None.

        Raises:
            BkwException: Handles BankruptcyWatch exceptions

        Returns:
            Result: A wrapper for the BankruptcyWatch request response
        """
        ep_params['OPERATION'] = operation
        ep_params['PROTOCOL'] = 'JSON'
        if not 'username' in ep_params: ep_params['username'] = self.username
        if not 'password' in ep_params: ep_params['password'] = self.password
        log_line_pre = f"method={http_method}, url={self.url}, params={ep_params}"

        # Log HTTP params and perform an HTTP request, catching and re-raising any exceptions
        try:
            self._logger.debug(msg=log_line_pre)
            response = requests.request(method=http_method, url=self.url, verify=self._ssl_verify, params=ep_params, json=data)
        except requests.exceptions.RequestException as e:
            self._logger.error(msg=(str(e)))
            raise BkwException("Request failed") from e

        # Deserialize JSON output to Python object, or return failed Result on exception
        try:
            bkw_response = response.json()
        except (ValueError, JSONDecodeError) as e:
            self._logger.error(msg=', '.join(log_line_pre, "success=False, status_code=None, message={e}"))
            raise BkwException("Bad JSON in response") from e
        
        result = Result(http_status_code=response.status_code, http_message=response.reason, bkw_response=bkw_response)
        log_line = ', '.join((log_line_pre, "http_status_code={result.http_status_code}, http_message={result.http_message} bkw_status_code={result.bkw_status_code}, bkw_message={result.bkw_message}, response={result.bkw_response}"))

        # Handle HTTP errors
        if 299 < result.http_status_code < 200:
            self._logger.error(msg=log_line)
            raise BkwException(f"{result.http_status_code}: {result.http_message}")
        
        # Handle BKW errors
        if result.bkw_status_code != 0:
            self._logger.error(msg=log_line)
            raise BkwException(f"{result.bkw_status_code}: {result.bkw_message}")
        
        self._logger.debug(msg=log_line)
        return result
        

    def get(self, operation: str, ep_params: Dict = {}) -> Result:
        """Returns a GET request to the BankruptcyWatch API.

        Args:
            operation (str): The BankruptcyWatch operation e.g. ListDistricts
            ep_params (Dict, optional): The BankruptcyWatch parameters. Defaults to {}.

        Returns:
            Result: A wrapper for the BankruptcyWatch request response
        """
        return self._do(http_method='GET', operation=operation, ep_params=ep_params)

    def post(self, operation: str, ep_params: Dict = {}, data: Dict = None) -> Result:
        """Returns a POST request to the BankruptcyWatch API.

        Args:
            operation (str): The BankruptcyWatch operation e.g. ListDistricts
            ep_params (Dict, optional): The BankruptcyWatch parameters. Defaults to {}.
            data (Dict, optional): The data included for a PUT request. Defaults to None.

        Returns:
            Result: A wrapper for the BankruptcyWatch request response
        """
        return self._do(http_method='POST', operation=operation, ep_params=ep_params, data=data)
