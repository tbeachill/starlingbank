from requests import get, put
from uuid import uuid4
from json import dumps as json_dumps
from base64 import b64decode
from typing import Dict
from .constants import *
from .utils import _url
from typing import List

class SavingSpace:
    """Representation of a Saving Space."""
    
    def __init__(
        self, auth_headers: Dict, sandbox: bool, account_uid: str
    ) -> None:
        self._auth_headers = auth_headers
        self._sandbox = sandbox
        self._account_uid = account_uid

        self.uid = None
        self.name = None
        self.target_currency = None
        self.target_minor_units = None
        self.total_saved_currency = None
        self.total_saved_minor_units = None
        self.saved_percentage = None
        self.sort_order = None
        self.state = None
        
        # Recurring Transfer Data
        self.transfer_uid = None
        self.reccurence_rule = {} # type: Dict[str, str]
        self.next_payment_date = None
        self.currency = None
        self.minor_units = None
        
    def update(self, space: Dict = None) -> None:
        """Update a single Saving Space."""
        if space is None:
            endpoint = "/account/{0}/savings-goals/{1}".format(
                self._account_uid, self.uid
            )
            response = get(
                _url(endpoint, self._sandbox), headers=self._auth_headers
            )
            response.raise_for_status()
            space = response.json()

        self.uid = space.get("savingsGoalUid")
        self.name = space.get("name")

        target = space.get("target", {})
        self.target_currency = target.get("currency")
        self.target_minor_units = target.get("minorUnits")

        total_saved = space.get("totalSaved", {})
        self.total_saved_currency = total_saved.get("currency")
        self.total_saved_minor_units = total_saved.get("minorUnits")
        
        self.saved_percentage = space.get("savedPercentage")
        self.state = space.get("state")
        self.sort_order = space.get("sortOrder")
        self._update_transfer_data()
        
    def _update_transfer_data(self) -> None:
        """Update the recurring transfer rules for a single Saving Space."""
        endpoint = "/account/{0}/savings-goals/{1}/recurring-transfer".format(
            self._account_uid, self.uid
        )
        response = get(
            _url(endpoint, self._sandbox), headers=self._auth_headers
        )
        if response.status_code == 404:
            return
        
        response.raise_for_status()
        space = response.json()

        self.transfer_uid = space.get("transferUid")
        self.recurrence_rule = space.get("recurrenceRule", {})
        self.next_payment_date = space.get("nextPaymentDate")
        
        currency_amount = space.get("currencyAndAmount", {})
        self.currency = currency_amount.get("currency")
        self.minor_units = currency_amount.get("minorUnits")  
        
    def deposit(self, deposit_minor_units: int) -> None:
        """Add funds to a Saving Space."""
        endpoint = "/account/{0}/savings-goals/{1}/add-money/{2}".format(
            self._account_uid, self.uid, uuid4()
        )

        body = {
            "amount": {
                "currency": self.total_saved_currency,
                "minorUnits": deposit_minor_units,
            }
        }

        response = put(
            _url(endpoint, self._sandbox),
            headers=self._auth_headers,
            data=json_dumps(body),
        )
        response.raise_for_status()

        self.update()

    def withdraw(self, withdraw_minor_units: int) -> None:
        """Withdraw funds from a Saving Space."""
        endpoint = "/account/{0}/savings-goals/{1}/withdraw-money/{2}".format(
            self._account_uid, self.uid, uuid4()
        )

        body = {
            "amount": {
                "currency": self.total_saved_currency,
                "minorUnits": withdraw_minor_units,
            }
        }

        response = put(
            _url(endpoint, self._sandbox),
            headers=self._auth_headers,
            data=json_dumps(body),
        )
        response.raise_for_status()

        self.update()

    def get_image(self, filename: str = None) -> None:
        """Download the photo associated with a Saving Space."""
        if filename is None:
            filename = "{0}.png".format(self.name)

        endpoint = "/account/{0}/savings-goals/{1}/photo".format(
            self._account_uid, self.uid
        )

        response = get(
            _url(endpoint, self._sandbox), headers=self._auth_headers
        )
        response.raise_for_status()

        base64_image = response.json()["base64EncodedPhoto"]
        with open(filename, "wb") as file:
            file.write(b64decode(base64_image))
