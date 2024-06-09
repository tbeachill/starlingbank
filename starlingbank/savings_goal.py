from requests import get, put
from uuid import uuid4
from json import dumps as json_dumps
from base64 import b64decode
from typing import Dict
from .constants import *
from .utils import _url
from typing import List

class SavingsGoal:
    """Representation of a Savings Goal (Saving Space)."""
    
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
        self.transfer_uid = None
        
        # Recurring Transfer Data
        self.recurrence_start_date = None
        self.recurrence_frequency = None
        self.recurrence_interval = None
        self.recurrence_count = None
        self.recurrence_until_date = None
        self.recurrence_week_start = None
        self.recurrence_days = [] # type: List[str]
        self.recurrence_month_day = None
        self.recurrence_month_week = None
        
        self.next_payment_date = None
        self.currency = None
        self.minor_units = None
        self.top_up = None
        
    def update(self, goal: Dict = None) -> None:
        """Update a single Savings Goal."""
        if goal is None:
            endpoint = "/account/{0}/savings-goals/{1}".format(
                self._account_uid, self.uid
            )
            response = get(
                _url(endpoint, self._sandbox), headers=self._auth_headers
            )
            response.raise_for_status()
            goal = response.json()

        self.uid = goal.get("savingsGoalUid")
        self.name = goal.get("name")

        target = goal.get("target", {})
        self.target_currency = target.get("currency")
        self.target_minor_units = target.get("minorUnits")

        total_saved = goal.get("totalSaved", {})
        self.total_saved_currency = total_saved.get("currency")
        self.total_saved_minor_units = total_saved.get("minorUnits")
        
        self.saved_percentage = goal.get("savedPercentage")
        self.state = goal.get("state")
        self.sort_order = goal.get("sortOrder")
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
        goal = response.json()

        self.transfer_uid = goal.get("transferUid")
        self.next_payment_date = goal.get("nextPaymentDate")
        self.top_up = goal.get("topUp")
        
        recurrence = goal.get("recurrenceRule", {})
        self.recurrence_start_date = recurrence.get("startDate")
        self.recurrence_frequency = recurrence.get("frequency")
        self.recurrence_interval = recurrence.get("interval")
        self.recurrence_count = recurrence.get("count")
        self.recurrence_until_date = recurrence.get("untilDate")
        self.recurrence_week_start = recurrence.get("weekStart")
        self.recurrence_days = recurrence.get("days", [])
        self.recurrence_month_day = recurrence.get("monthDay")
        self.recurrence_month_week = recurrence.get("monthWeek")
        
        currency_amount = goal.get("currencyAndAmount", {})
        self.currency = currency_amount.get("currency")
        self.minor_units = currency_amount.get("minorUnits")
        
    def deposit(self, deposit_minor_units: int) -> None:
        """Add funds to a Savings Goal."""
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
        """Withdraw funds from a Savings Goal."""
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
        """Download the photo associated with a Savings Goal."""
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
