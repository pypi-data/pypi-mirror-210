import pytest
import requests
import json
from typing import List
from pydantic import parse_obj_as
from bkw_python import BkwApi, BkwException
from bkw_python.data_models import Case

# TODO: Add versioning to client in these test cases

def test_run_parse_document_no_secured_claims(requests_mock):
    with open('tests/document_parsing_responses/22_24902_no_secured_claims.json') as resp:
        resp_json = resp.read()
    requests_mock.get(
        "https://api.bk.watch/api/2022-08-01?username=test&password=password&PROTOCOL=JSON&OPERATION=ParseDocuments&district=UT&extendedCaseNumber=2%3A22-bk-24902&cache=true", 
        json=json.loads(resp_json)
    )
    testing_session = BkwApi(username='test', password='password')
    case, bkml = testing_session.parse_document(district='UT', extendedCaseNumber='2:22-bk-24902', cache=True)
    assert case.id == 'case-2f190a12'
    assert bkml.form106D
    assert not bkml.form106D.get_secured_claims()

def test_run_parse_document_secured_claims(requests_mock):
    with open('tests/document_parsing_responses/18_42694_secured_claims.json') as resp:
        resp_json = resp.read()
    requests_mock.get(
        "https://api.bk.watch/api/2022-08-01?username=test&password=password&PROTOCOL=JSON&OPERATION=ParseDocuments&district=TXE&extendedCaseNumber=4%3A18-bk-42694&cache=true", 
        json=json.loads(resp_json)
    )
    testing_session = BkwApi(username='test', password='password')
    case, bkml = testing_session.parse_document(district='TXE', extendedCaseNumber='4:18-bk-42694', cache=True)
    assert case.id == 'case-678b19c5'
    assert bkml.form106D
    assert bkml.form106D.get_secured_claims()
    assert bkml.form106D.get_secured_claims()[0].amount == "12540.00"
    assert bkml.form106D.get_secured_claims()[0].collateral == "12900.00"
    assert bkml.form106D.get_secured_claims()[1].amount == "215009.37"
    assert bkml.form106D.get_secured_claims()[1].collateral == "607000.00"
    assert bkml.form106D.get_secured_claims()[2].amount == "21368.42"
    assert bkml.form106D.get_secured_claims()[2].collateral == "21368.42"
