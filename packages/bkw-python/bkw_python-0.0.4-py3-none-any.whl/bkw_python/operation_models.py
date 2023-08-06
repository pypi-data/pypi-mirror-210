from __future__ import annotations
from typing import Optional, List, Tuple
import xmltodict as xd
from pydantic import parse_obj_as, ValidationError
from .exceptions import BkwException
from .rest_adapter import RestAdapter
from .data_models import Case, Party, Bkml
import logging

class BkwApi:
    def __init__(self, hostname: str = 'api.bk.watch/api', ver: str = '2022-08-01', username: str = "", password: str = "", ssl_verify: bool = True, logger: logging.Logger = None):
        self._logger = logger or logging.getLogger(__name__)
        self._rest_adapter = RestAdapter(hostname, ver, username, password, ssl_verify, logger)

    def run_docket(self, district: str, extendedCaseNumber: str, fromDate: Optional[str] = '', toDate: Optional[str] = '', fromItem: Optional[int] = None, toItem: Optional[int] = None, pacerAccount: Optional[str] = '', cache: bool = True) -> Case:
        ep_params = {
            'district': district,
            'extendedCaseNumber': extendedCaseNumber,
            'dateType': 'filed',
        }
        if cache: ep_params['cache'] = 'true'
        if not cache: ep_params['cache'] = 'false'
        if fromDate: ep_params['fromDate'] = fromDate
        if toDate: ep_params['toDate'] = toDate
        if fromItem: ep_params['fromItem'] = fromItem
        if toItem: ep_params['toItem'] = toItem
        if pacerAccount: ep_params['pacerAccount'] = pacerAccount
        result = self._rest_adapter.get(operation="RunDocket", ep_params=ep_params)
        if (not result.bkw_response) or (not 'case' in result.bkw_response):
            self._logger.warning(msg="No results found from the request.")
            raise BkwException("No case found.")
        return Case.parse_obj(result.bkw_response['case'])
    
    def parse_document(self, district: str, extendedCaseNumber: str, documentIds: Optional[str] = '', formNumbers: Optional[str] = '', pacerAccount: Optional[str] = '', cache: bool = True) -> Tuple[Case, Bkml]:
        ep_params = {
            'district': district,
            'extendedCaseNumber': extendedCaseNumber,
        }
        if cache: ep_params['cache'] = 'true'
        if not cache: ep_params['cache'] = 'false'
        if documentIds: ep_params['documentIds'] = documentIds
        if formNumbers: ep_params['formNumbers'] = formNumbers
        if pacerAccount: ep_params['pacerAccount'] = pacerAccount
        result = self._rest_adapter.get(operation="ParseDocuments", ep_params=ep_params)
        if (not result.bkw_response) or (not 'case' in result.bkw_response):
            self._logger.warning(msg="No results found from the request.")
            raise BkwException("No case found.")
        case = Case.parse_obj(result.bkw_response['case'])
        bkml = Bkml.parse_obj(xd.parse(result.bkw_response['data'])['bkml'])
        return (case, bkml)
        
    def run_claims_register(self, district: str, extendedCaseNumber: str, fromDate: Optional[str] = '', toDate: Optional[str] = '', fromClaim: Optional[int] = None, toClaim: Optional[int] = None, pacerAccount: Optional[str] = '', cache: Optional[bool] = True) -> Case:
        ep_params = {
            'district': district,
            'extendedCaseNumber': extendedCaseNumber,
        }
        if cache: ep_params['cache'] = 'true'
        if not cache: ep_params['cache'] = 'false'
        if fromDate: ep_params['fromDate'] = fromDate
        if toDate: ep_params['toDate'] = toDate
        if fromClaim: ep_params['fromClaim'] = fromClaim
        if toClaim: ep_params['toClaim'] = toClaim
        if pacerAccount: ep_params['pacerAccount'] = pacerAccount
        result = self._rest_adapter.get(operation="RunClaimsRegister", ep_params=ep_params)
        if (not result.bkw_response) or (not 'case' in result.bkw_response):
            self._logger.warning(msg="No case found in the response.")
            raise BkwException("No case found.")
        return Case.parse_obj(result.bkw_response['case'])

    def search_cases(
        self, 
        start: int = 1, 
        end: int = 50, 
        outputFormat: Optional[str] = None, 
        districts: Optional[List[str]] = [],
        chapters: Optional[List[int]] = [],
        event: Optional[str] = None,
        eventAfter: Optional[str] = None,  # TODO: show that it could be equal to
        eventBefore: Optional[str] = None,
        filters: Optional[List[str]] = None,
        ) -> List[Case]:
        """Gets a list of BankruptcyWatch cases matching the filter criteria.

        Your account must have access to the SearchCases operation. Request access by contacting us at www.BankruptcyWatch.com.

        Args:
            start (int, optional): The 1-based offset of the first party to be returned, within the collection of all parties matching the search criteria. Defaults to 1.
            end (int, optional): The 1-based offset of the last party to be returned, within the collection of all parties matching the search criteria; the search may return fewer parties than requested. Defaults to 50. Max value is start + 200.
            outputFormat (Optional[str], optional): A whitespace-separated list of output format names (see docs). Defaults to None which ends up being document when passed through the API.
            districts (Optional[List[str]], optional): A list of district codes to filter results. Defaults to [].
            chapters (Optional[List[int]], optional): A list of chapters to filter results. Defaults to [].
            event (Optional[str], optional): The event to search for. Current options include dateFiled, dateDismissed, dateDischarged, dateConverted. More in the docs. Defaults to None.
            eventAfter (Optional[str], optional): Date to start filtering the event specified above. Requires the event parameter. Inclusive. Defaults to None. Formatted YYYY-MM-DD.
            eventBefore (Optional[str], optional): Date to end filtering the event specified above. Requires the event parameter. Inclusive. Defaults to None. Formatted YYYY-MM-DD.
            filters: (Optional[List[str]], optional): Additional BankruptcyWatch filters requested. Defaults to None. Formatted as a list of filter strings.

        Returns:
            List[Case]: Returns a list of matching cases.
        """
        ep_params={'filters[]': []}
        ep_params['from'] = start
        ep_params['to'] = end
        if outputFormat: ep_params['outputFormat'] = outputFormat
        if districts: ep_params['filters[]'].append("district,in," + ",".join(districts))
        if chapters: ep_params['filters[]'].append("chapter,in," + ",".join([str(c) for c in chapters]))
        if event and eventAfter: ep_params['filters[]'].append(event + ",ge," + eventAfter)
        if event and eventBefore: ep_params['filters[]'].append(event + ",le," + eventBefore)
        if filters: ep_params['filters[]'].extend(filters)
        
        result = self._rest_adapter.get(operation = "SearchCases", ep_params=ep_params)
        if (not result.bkw_response) or (not 'results' in result.bkw_response):
            self._logger.warning(msg="No results found from the request")
            return []
        if not 'items' in result.bkw_response['results']:
            self._logger.warning(msg="No items found in found from the request.")
            return []
        try:
            return parse_obj_as(List[Case], result.bkw_response['results']['items'])
        except ValidationError as e:
            raise ValidationError from e

    def search_parties(
        self, 
        start: int = 1, 
        end: int = 50,
        outputFormat: Optional[str] = None, 
        districts: Optional[List[str]] = [],
        chapters: Optional[List[int]] = [],
        event: Optional[str] = None,
        eventAfter: Optional[str] = None,  # TODO: show that it could be equal to
        eventBefore: Optional[str] = None,
        filters: Optional[List[str]] = None,
    ) -> List[Party]:
        """Gets a list of BankruptcyWatch parties matching the filter criteria. 
        
        NOTE: this operation is very slow with and doesn't include attorney + case information in queries many queries. It is recommended to get the party ID from 
        SearchParties with the outputFormat parameter set to "parties" and use this operation to attach attorneys if necessary.

        Args:
            start (int, optional): The 1-based offset of the first party to be returned, within the collection of all parties matching the search criteria. Defaults to 1.
            end (int, optional): The 1-based offset of the last party to be returned, within the collection of all parties matching the search criteria; the search may return fewer parties than requested. Defaults to 50. Max value is start + 200.
            outputFormat (Optional[str], optional): A whitespace-separated list of output format names (see docs). Defaults to None which ends up being document when passed through the API.
            districts (Optional[List[str]], optional): A list of district codes to filter results. Defaults to [].
            chapters (Optional[List[int]], optional): A list of chapters to filter results. Defaults to [].
            event (Optional[str], optional): The event to search for. Current options include dateFiled, dateDismissed, dateDischarged, dateConverted. More in the docs. Defaults to None.
            eventAfter (Optional[str], optional): Date to start filtering the event specified above. Defaults to None.
            eventBefore (Optional[str], optional): Date to end filtering the event specified above. Defaults to None.
            filters: (Optional[List[str]], optional): Additional BankruptcyWatch filters requested. Defaults to None. Formatted as a list of filter strings.

        Returns:
            List[Case]: Returns a list of matching cases.
        """
        ep_params={'filters[]': []}
        if outputFormat: ep_params['outputFormat'] = outputFormat
        ep_params['from'] = start
        ep_params['to'] = end
        if districts: ep_params['filters[]'].append("case.district,in," + ",".join(districts))
        if chapters: ep_params['filters[]'].append("case.chapter,in," + ",".join([str(c) for c in chapters]))
        if event and eventAfter: ep_params['filters[]'].append("case." + event + ",ge," + eventAfter)
        if event and eventBefore: ep_params['filters[]'].append("case." + event + ",le," + eventBefore)
        if filters: ep_params['filters[]'].extend(filters)

        result = self._rest_adapter.get(operation = "SearchParties", ep_params=ep_params)
        if (not result.bkw_response) or (not 'results' in result.bkw_response):
            self._logger.warning(msg="No results found from the request")
            return []
        if not 'items' in result.bkw_response['results']:
            self._logger.warning(msg="No items found in found from the request.")
            return []
        try:
            return parse_obj_as(List[Party], result.bkw_response['results']['items'])
        except ValidationError as e:
            raise ValidationError from e
