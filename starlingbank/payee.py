from typing import List, Dict
from .constants import *
from .utils import _url
from requests import get

class Payee:
    """Representation of a payee."""
        
    def __init__(
        self, auth_headers: Dict, sandbox: bool, account_uid: str,
        payee_uid: str
    ) -> None:
        self._auth_headers = auth_headers       
        self._sandbox = sandbox
        self._account_uid = account_uid

        # Payee Data
        self.uid = payee_uid
        self.name = None
        self.phone_number = None
        self.type = None
        self.first_name = None
        self.middle_name = None
        self.last_name = None
        self.business_name = None
        self.date_of_birth = None
        
        self.payee_accounts = {} # type: Dict[str, PayeeAccount]
        
        
    def update(self) -> None:
        """Update payee."""
        response = get(
            _url("/payees".format(), self._sandbox),
            headers=self._auth_headers
        )
        response.raise_for_status()
        response = response.json()
        
        for payee in response.get("payees", []):
            if payee.get("payeeUid") == self.uid:
                self.name = payee.get("payeeName")
                self.phone_number = payee.get("phoneNumber")
                self.type = payee.get("payeeType")
                self.first_name = payee.get("firstName")
                self.middle_name = payee.get("middleName")
                self.last_name = payee.get("lastName")
                self.business_name = payee.get("businessName")
                self.date_of_birth = payee.get("dateOfBirth")
                
                for account in payee.get("accounts", []):
                    payee_account_uid = account.get("payeeAccountUid")
                    self.payee_accounts[payee_account_uid] = PayeeAccount(
                        self._auth_headers, self._sandbox, self._account_uid,
                        payee_account_uid
                    )
                    self.payee_accounts[payee_account_uid].update(response, self.uid)
                return

class PayeeAccount:
    """Representation of a payee account."""
    
    def __init__(
        self, auth_headers: Dict, sandbox: bool, account_uid: str,
        payee_account_uid: str
    ) -> None:
        self._auth_headers = auth_headers       
        self._sandbox = sandbox
        self._account_uid = account_uid

        # Payee Account Data
        self.account_uid = payee_account_uid
        self.channel_type = None
        self.description = None
        self.default_account = None
        self.country_code = None
        self.account_identifier = None
        self.bank_identifier = None
        self.bank_identifier_type = None
        self.last_references = [] # type: List[str]
        
    def update(self, response, payee_uid) -> None:
        for payee in response.get("payees", []):
            if payee.get("payeeUid") == payee_uid:
                for account in payee.get("accounts", []):
                    self.channel_type = account.get("channelType")
                    self.description = account.get("description")
                    self.default_account = account.get("defaultAccount")
                    self.country_code = account.get("countryCode")
                    self.account_identifier = account.get("accountIdentifier")
                    self.bank_identifier = account.get("bankIdentifier")
                    self.bank_identifier_type = account.get("bankIdentifierType")
                    self.last_references = account.get("lastReferences")
                return
