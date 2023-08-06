import pytest
import requests
import json
from typing import List
from pydantic import parse_obj_as
from bkw_python import BkwApi, BkwException
from bkw_python.data_models import Case, Bkml

# TODO: Add versioning to client in these test cases

def test_run_parse_document_schedule_i_multiple_income(requests_mock):
    with open('tests/document_parsing_responses/20-40596-schedule-i.json') as resp:
        resp_json = resp.read()
    requests_mock.get(
        "https://api.bk.watch/api/2022-08-01?district=TXN&extendedCaseNumber=4%3A20-bk-40596&cache=true&formNumbers=I&OPERATION=ParseDocuments&PROTOCOL=JSON&username=test&password=password",
        json=json.loads(resp_json),
    )
    testing_session = BkwApi(username='test', password='password')
    case, bkml = testing_session.parse_document(district='TXN', extendedCaseNumber='4:20-bk-40596', formNumbers="I", cache=True)
    assert case.id == 'case-83694610'
    assert bkml
    assert bkml.formIm[0].document
    assert bkml.formIm[0].data.employment.debtor1.employerName
    assert not bkml.formIm[0].data.employment.debtor2.employerName
    assert bkml.formIm[2].data.income.line10.total

def test_run_parse_document_schedule_i_basic_single_income(requests_mock):
    with open('tests/document_parsing_responses/22-20465-schedule-i.json') as resp:
        resp_json = resp.read()
    requests_mock.get(
        "https://api.bk.watch/api/2022-08-01?district=UT&extendedCaseNumber=2%3A22-bk-20465&cache=true&formNumbers=I&OPERATION=ParseDocuments&PROTOCOL=JSON&username=test&password=password",
        json=json.loads(resp_json),
    )
    testing_session = BkwApi(username='test', password='password')
    case, bkml = testing_session.parse_document(district='UT', extendedCaseNumber='2:22-bk-20465', formNumbers="I", cache=True)
    assert case.id == 'case-2f103c62'
    assert bkml
    assert bkml.formIm.document
    assert bkml.formIm.data.employment.debtor1.employerName
    assert bkml.formIm.data.employment.debtor2.employerName
    assert bkml.formIm.data.income.line10.total