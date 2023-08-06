import pytest
import requests
from typing import List
from pydantic import parse_obj_as
from bkw_python import BkwApi
from bkw_python.data_models import Case, Party

# TODO: Add versioning to client in these test cases

def test_search_parties_simple(requests_mock):
    requests_mock.get(
        "https://api.bk.watch/api/2022-08-01?username=test&password=password&PROTOCOL=JSON&OPERATION=SearchParties&filters%5B%5D=case.district%2Cin%2CAK&from=1&to=2", 
        json={'results': {'items': [{'id': 'party-a1143166', 'role': 'JUDGE', 'name': 'Herbert A Ross', 'address': {'firstName': 'Herbert', 'middleName': 'A', 'lastName': 'Ross'}}, {'id': 'party-67a9ecf5', 'role': 'JUDGE', 'name': 'Gary Spraker', 'address': {'firstName': 'Gary', 'lastName': 'Spraker'}}], 'offset': 1, 'total': 9950}, 'status': 0, 'message': 'Success'}
    )
    testing_session = BkwApi(username='test', password='password')
    parties = testing_session.search_parties(start=1, end=2, districts=['AK'])
    assert len(parties) == 2
    assert parties[0].id == "party-a1143166"
    assert parties[0].role == "JUDGE"
    assert parties[1].id == "party-67a9ecf5"
    assert parties[1].role == "JUDGE"

def test_search_parties_case_filter(requests_mock):
    requests_mock.get(
        "https://api.bk.watch/api/2022-08-01?username=test&password=password&PROTOCOL=JSON&OPERATION=SearchParties&filters%5B%5D=case.id%2Cin%2Ccase-2f1baa62&from=1&to=1", 
        json={'results': {'items': [{'id': 'party-360583ae', 'role': 'JUDGE', 'name': 'R. Kimball Mosier', 'address': {'firstName': 'R.', 'middleName': 'Kimball', 'lastName': 'Mosier'}}], 'offset': 1, 'total': 4}, 'status': 0, 'message': 'Success'}
    )
    testing_session = BkwApi(username='test', password='password')
    parties = testing_session.search_parties(start=1, end=1, filters=['case.id,in,case-2f1baa62'])
    assert len(parties) == 1
    assert parties[0].id == "party-360583ae"
    assert parties[0].role == "JUDGE"

def test_search_parties_output_attorney(requests_mock):
    requests_mock.get(
        "https://api.bk.watch/api/2022-08-01?username=test&password=password&PROTOCOL=JSON&OPERATION=SearchParties&filters%5B%5D=case.id%2Cin%2Ccase-2f1baa62&from=1&to=1", 
        json={'results': {'items': [{'id': 'party-360583ae', 'role': 'JUDGE', 'name': 'R. Kimball Mosier', 'address': {'firstName': 'R.', 'middleName': 'Kimball', 'lastName': 'Mosier'}}], 'offset': 1, 'total': 4}, 'status': 0, 'message': 'Success'}
    )
    testing_session = BkwApi(username='test', password='password')
    parties = testing_session.search_parties(start=1, end=1, filters=['case.id,in,case-2f1baa62'])
    assert len(parties) == 1
    assert parties[0].id == "party-360583ae"
    assert parties[0].role == "JUDGE"