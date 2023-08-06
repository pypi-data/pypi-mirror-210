from __future__ import annotations
from typing import Optional, List
from typing import List, Dict, Union
from datetime import datetime
from pydantic import BaseModel, validator

class Address(BaseModel):
    """
    BankruptcyWatch API Address definition

    https://docs.bk.watch/api/2021-11-01/ref/#addresses.page.html
    """
    prefix: Optional[str] = None
    firstName: Optional[str] = None
    middleName: Optional[str] = None
    lastName: Optional[str] = None
    generation: Optional[str] = None
    title: Optional[str] = None
    organization: Optional[str] = None
    attention: Optional[str] = None
    careOf: Optional[str] = None
    street1: Optional[str] = None
    street2: Optional[str] = None
    street3: Optional[str] = None
    city: Optional[str] = None
    county: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None  # TODO: make sure not an int
    zip4: Optional[str] = None # TODO: make sure not an int
    country: Optional[str] = None
    phone1: Optional[str] = None  # TODO: make sure not an int
    phone2: Optional[str] = None  # TODO: make sure not an int
    phone3: Optional[str] = None  # TODO: make sure not an int
    fax: Optional[str] = None  # TODO: make sure not an int
    email: Optional[str] = None
    latitude: Optional[str] = None  # TODO: make sure not a float
    longitude: Optional[str] = None   # TODO: make sure not an float
    ssn: Optional[str] = None
    eins: Optional[str] = None
    url: Optional[str] = None

class Case(BaseModel):
    """
    BankruptcyWatch API Case definition

    https://docs.bk.watch/api/2021-11-01/ref/#cases.page.html
    """
    id: str
    district: str
    division: str
    caseNumber: str 
    county: Optional[str] = None
    title: Optional[str] = None
    chapter: Optional[int] = None
    previousChapter: Optional[int] = None
    dateClosed: Optional[datetime] = None
    dateConverted: Optional[datetime] = None
    dateDischarged: Optional[datetime] = None
    dateDismissed: Optional[datetime] = None
    dateEntered: Optional[datetime] = None
    dateFiled: Optional[datetime] = None
    dateJointDebtorDischarged: Optional[datetime] = None
    dateJointDebtorDismissed: Optional[datetime] = None
    datePlanConfirmed: Optional[datetime] = None
    dateReopened: Optional[datetime] = None
    dateTerminated: Optional[datetime] = None
    dateTransferred: Optional[datetime] = None
    lastDateToFileClaims: Optional[datetime] = None
    lastDateToFileClaimsGovt: Optional[datetime] = None
    closed: Optional[bool] = None
    disposition: Optional[str] = None
    jointDebtorDisposition: Optional[str] = None
    filingFeeStatus: Optional[str] = None
    assets: Optional[bool] = None
    voluntary: Optional[bool] = None
    debtorType: Optional[str] = None
    debtType: Optional[str] = None
    parties: Optional[List[Party]] = None
    claims: Optional[List[Claim]] = None
    creditors: Optional[List[Creditor]] = None
    docketItems: Optional[List[Filing]] = None
    data: Optional[str] = None

    @validator(
        "dateClosed", 
        "dateConverted", 
        "dateDischarged", 
        "dateDismissed", 
        "dateFiled", 
        "dateEntered", 
        "dateJointDebtorDischarged", 
        "dateJointDebtorDismissed", 
        "datePlanConfirmed", 
        "dateReopened", 
        "dateTerminated", 
        "dateTransferred", 
        "lastDateToFileClaims", 
        "lastDateToFileClaimsGovt", 
        pre=True
    )
    def parse_date(cls, value):
        return datetime.strptime(
            value,
            "%Y-%m-%d"
        )


class Claim(BaseModel):
    """
    BankruptcyWatch API Claim definition

    https://docs.bk.watch/api/2021-11-01/ref/#claims.page.html
    """
    id: str
    case: Optional[Case]
    claimNumber: int
    creditor: Creditor
    dateFiled: Optional[datetime]
    amendedDateFiled: Optional[datetime]
    dateModified: Optional[datetime]
    unsecuredClaimed: Optional[float]
    securedClaimed: Optional[float]
    priorityClaimed: Optional[float]
    unknownClaimed: Optional[float]
    administrativeClaimed: Optional[float]
    totalClaimed: Optional[float]
    unsecuredAllowed: Optional[float]
    securedAllowed: Optional[float]
    priorityAllowed: Optional[float]
    unknownAllowed: Optional[float]
    administrativeAllowed: Optional[float]
    totalAllowed: Optional[float]
    statusText: Optional[str]
    filings: List[Filing]

    @validator("dateFiled", "amendedDateFiled", "dateModified", pre=True)
    def parse_date(cls, value):
        return datetime.strptime(
            value,
            "%Y-%m-%d"
        )


class Creditor(BaseModel):
    """
    BankruptcyWatch API Creditor definition

    https://docs.bk.watch/api/2021-11-01/ref/#creditors.page.html
    """
    id: Optional[str]
    case: Optional[Case]
    name: Optional[str]
    creditorNumber: Optional[int]
    address: Optional[Address]


class Document(BaseModel):
    """
    BankruptcyWatch API Document definition

    https://docs.bk.watch/api/2021-11-01/ref/#documents.page.html
    """
    id: str
    title: Optional[str]
    description: Optional[str]
    created: datetime
    contentType: Optional[str]
    charset: Optional[str]
    language: Optional[str]
    size: Optional[int]
    sha1: Optional[str]
    metadata: Optional[List[dict]]  # TODO: parse the name values
    url: Optional[str]

    @validator("created", pre=True)
    def parse_date(cls, value):
        return datetime.strptime(
            value,
            "%Y-%m-%d"
        )


class Filing(BaseModel):
    """
    BankruptcyWatch API Filing definition

    https://docs.bk.watch/api/2021-11-01/ref/#filings.page.html
    """
    id: str
    case: Optional[Case]
    type: Optional[str]
    dateFiled: Optional[datetime]
    claimNumber: Optional[int]
    itemNumber: Optional[int]
    title: Optional[str]
    text: Optional[str]
    url: Optional[str]
    documents: Optional[List[Document]]

    @validator("dateFiled", pre=True)
    def parse_date(cls, value):
        return datetime.strptime(
            value,
            "%Y-%m-%d"
        )


class Party(BaseModel):
    """
    BankruptcyWatch API Party definition

    https://docs.bk.watch/api/2021-11-01/ref/#parties.page.html
    """
    id: Optional[str] = None
    case: Optional[Case]  # TODO: the documentation needs to be updated because this is clearly optional
    role: Optional[str]  # TODO: the documentation needs to be updated because this is optional in the response from SearchParties
    name: Optional[str]  # TODO: the documentation needs to be updated because this is optional in the response from SearchParties
    address: Optional[Address]  # TODO: the documentation needs to be updated because this is optional in the response from SearchParties
    partyNumber: Optional[int] = None
    dateAdded: Optional[datetime] = None
    dateTerminated: Optional[datetime] = None
    attorneys: Optional[List[Party]]

    @validator("dateAdded", "dateTerminated", pre=True)
    def parse_date(cls, value):
        return datetime.strptime(
            value,
            "%Y-%m-%d"
        )

class Bkml(BaseModel):
    form106D: Optional[Form106D]
    formIm: Optional[Union[FormIm, List[FormIm]]]

class FormIm(BaseModel):
    document: Optional[str]
    page: Optional[str]
    data: Optional[FormImData]

class FormImData(BaseModel):
    maritalStatus: Optional[str]
    employment: Optional[FormImEmployment]
    income: Optional[FormImIncome]

class FormImEmployment(BaseModel):
    debtor1: Optional[FormImDebtorEmployment]
    debtor2: Optional[FormImDebtorEmployment]

class FormImIncome(BaseModel):
    line2: Optional[FormImDebtorIncome]
    line3: Optional[FormImDebtorIncome]
    line4: Optional[FormImDebtorIncome]
    line5a: Optional[FormImDebtorIncome]
    line5b: Optional[FormImDebtorIncome]
    line5c: Optional[FormImDebtorIncome]
    line5d: Optional[FormImDebtorIncome]
    line5e: Optional[FormImDebtorIncome]
    line5f: Optional[FormImDebtorIncome]
    line5g: Optional[FormImDebtorIncome]
    line5h: Optional[Dict]
    line6: Optional[FormImDebtorIncome]
    line7: Optional[FormImDebtorIncome]
    line8a: Optional[FormImDebtorIncome]
    line8b: Optional[FormImDebtorIncome]
    line8c: Optional[FormImDebtorIncome]
    line8d: Optional[FormImDebtorIncome]
    line8e: Optional[FormImDebtorIncome]
    line8f: Optional[Dict]
    line8g: Optional[FormImDebtorIncome]
    line8h: Optional[Dict]
    line9: Optional[FormImDebtorIncome]
    line10: Optional[FormImDebtorIncome]
    line11: Optional[Dict]
    line12: Optional[str]
    line13: Optional[Dict]

class FormImDebtorIncome(BaseModel):
    debtor1: Optional[str]
    debtor2: Optional[str]
    total: Optional[str] # only happens in line 10 that I know of

class FormImDebtorEmployment(BaseModel):
    occupation: Optional[str]
    employerName: Optional[str]
    employerAddress: Optional[str]
    howLongEmployed: Optional[str]

class Form106D(BaseModel):
    document: Optional[str]
    page: Optional[str]
    data: Optional[Form106DData] = None

    def get_secured_claims(self) -> List[Form106DSecuredClaim]:
        secured_claims: Form106DSecuredClaim = []
        if self.data and self.data.part1 and self.data.part1.securedClaims and self.data.part1.securedClaims.claim: 
            if type(self.data.part1.securedClaims.claim) != list:  # Single claims aren't in a list
                secured_claims.append(self.data.part1.securedClaims.claim)
            else:
                secured_claims.extend(self.data.part1.securedClaims.claim)
        return secured_claims

class Form106DData(BaseModel):
    line1: Optional[bool]
    part1: Optional[Form106DDataPart1]
    part2: Optional[Dict]

class Form106DDataPart1(BaseModel):
    total: Optional[str]
    securedClaims: Optional[Form106DSecuredClaim]
    # securedClaims: Optional[Form106DSecuredClaim]

class Form106DSecuredClaim(BaseModel):
    claim: Optional[Union[Form106DClaim, List[Form106DClaim]]]

class Form106DClaim(BaseModel):
    page: Optional[str]
    line: Optional[str]
    creditorName: Optional[str]
    creditorAddress: Optional[str]
    debtor: Optional[str] # TODO: EDITED double check the model
    community: Optional[str]  # TODO: EDITED can pydantic convert to bool?
    date: Optional[str]
    description: Optional[str]
    contingent: Optional[str]  # TODO: EDITED can pydantic convert to bool?
    unliquidated: Optional[str] # TODO: EDITED can pydantic convert to bool?
    disputed: Optional[str]  # TODO: EDITED can pydantic convert to bool?
    natureOfLien: Optional[Dict]
    accountNumber: Optional[str]
    amount: Optional[str]
    collateral: Optional[str]
    unsecured: Optional[str]

Address.update_forward_refs()
Case.update_forward_refs()
Claim.update_forward_refs()
Creditor.update_forward_refs()
Document.update_forward_refs()
Filing.update_forward_refs()
Party.update_forward_refs()

Bkml.update_forward_refs()
FormIm.update_forward_refs()
FormImData.update_forward_refs()
FormImEmployment.update_forward_refs()
FormImDebtorEmployment.update_forward_refs()
FormImIncome.update_forward_refs()
FormImDebtorIncome.update_forward_refs()
Form106D.update_forward_refs()
Form106DData.update_forward_refs()
Form106DDataPart1.update_forward_refs()
Form106DSecuredClaim.update_forward_refs()