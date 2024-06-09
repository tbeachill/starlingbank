from typing import List, Dict
from .constants import *
from .utils import _url
from requests import get
from base64 import b64decode
from datetime import datetime, timedelta

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
                        payee_account_uid, self.uid
                    )
                    self.payee_accounts[payee_account_uid].update(response)
                return
            
    def get_payee_image(self, filename: str = None) -> str:
        """Get the payee image."""
        if filename is None:
            filename = "{0}.png".format(self.name)
            
        response = get(
            _url("/payees/{0}/image".format(
                self.uid), self._sandbox),
            headers=self._auth_headers
        )
        response.raise_for_status()
        
        base64_image = response.json()["base64EncodedPhoto"]
        with open(filename, "wb") as file:
            file.write(b64decode(base64_image))

class PayeeAccount:
    """Representation of a payee account."""
    
    def __init__(
        self, auth_headers: Dict, sandbox: bool, account_uid: str,
        payee_account_uid: str, payee_uid: str, payments_since: str = None
    ) -> None:
        self._auth_headers = auth_headers       
        self._sandbox = sandbox
        self._account_uid = account_uid

        # Payee Account Data
        self.account_uid = payee_account_uid
        self.payee_uid = payee_uid
        self.channel_type = None
        self.description = None
        self.default_account = None
        self.country_code = None
        self.account_identifier = None
        self.bank_identifier = None
        self.bank_identifier_type = None
        self.last_references = [] # type: List[str]
        
        self.payments = {} # type: Dict[str, PayeePayment]
        self.payments_since = payments_since
        
    def update(self, response) -> None:
        for payee in response.get("payees", []):
            if payee.get("payeeUid") == self.payee_uid:
                for account in payee.get("accounts", []):
                    if account.get("payeeAccountUid") == self.account_uid:
                        self.channel_type = account.get("channelType")
                        self.description = account.get("description")
                        self.default_account = account.get("defaultAccount")
                        self.country_code = account.get("countryCode")
                        self.account_identifier = account.get("accountIdentifier")
                        self.bank_identifier = account.get("bankIdentifier")
                        self.bank_identifier_type = account.get("bankIdentifierType")
                        self.last_references = account.get("lastReferences")
                        self._update_payee_payments()
                        return
                    
    def _update_payee_payments(self) -> None:
        """Get payee payments."""
        if self.payments_since is None:
            since_date = datetime.now() - timedelta(days=365)
            self.payments_since = since_date.strftime("%Y-%m-%d")
            
        response = get(
            _url("/payees/{0}/account/{1}/payments?since={2}".format(
                self.payee_uid, self.account_uid, self.payments_since), self._sandbox),
            headers=self._auth_headers
        )
        response.raise_for_status()
        response = response.json()
        
        for payment in response.get("payments", []):
            payment_uid = payment.get("paymentUid")
            self.payments[payment_uid] = PayeePayment(
                self._auth_headers, self._sandbox, self._account_uid,
                self.payee_uid, payment_uid, self.account_uid
            )
            self.payments[payment_uid].update(response)

class PayeePayment:
    """Representation of a payee payment."""
    
    def __init__(
        self, auth_headers: Dict, sandbox: bool, account_uid: str,
        payee_uid: str, payment_uid: str, payee_account_uid: str
    ) -> None:
        self._auth_headers = auth_headers       
        self._sandbox = sandbox
        self._account_uid = account_uid

        # Payee Payment Data
        self.payee_uid = payee_uid
        self.payment_uid = payment_uid
        self.payee_account_uid = payee_account_uid

        self.reference = None
        self.created_at = None
        self.spending_category = None
        self.currency = None
        self.minor_units = None     
        
    def update(self, response) -> None:
        """Update payee payment."""
        for payment in response.get("payments", []):
            if payment.get("paymentUid") == self.payment_uid:
                self.reference = payment.get("reference")
                self.created_at = payment.get("createdAt")
                self.spending_category = payment.get("spendingCategory")
                
                payment_amount = payment.get("paymentAmount")
                self.currency = payment_amount.get("currency")
                self.minor_units = payment_amount.get("minorUnits")
                return
