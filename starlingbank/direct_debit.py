from typing import Dict
from requests import get
from .utils import _url


class DirectDebit:
    """Representation of a direct debit mandate.

    Required Scopes:
        `mandate:read`

    Args:
        auth_headers (dict of {str, str}): Starling API authentication headers.
        sandbox (bool): True if sandbox mode, False otherwise.
        account_uid (str): Account UID.
        mandate_uid (str): Direct debit mandate UID.
    """

    def __init__(
        self, auth_headers: Dict, sandbox: bool, account_uid: str, mandate_uid: str
    ) -> None:
        self._auth_headers = auth_headers
        self._sandbox = sandbox
        self._account_uid = account_uid

        # Overall Data
        self.mandate_uid = mandate_uid
        self.reference = None
        self.status = None
        self.source = None
        self.created = None
        self.cancelled = None
        self.next_date = None
        self.last_date = None
        self.originator_name = None
        self.originator_uid = None
        self.merchant_uid = None
        self.category_uid = None

        # Last Payment Data
        self.last_payment_date = None
        self.last_payment_currency = None
        self.last_payment_minor_units = None

    def update(self) -> None:
        """Update mandate.

        Required Scopes:
            `mandate:read`
        """
        response = get(
            _url(f"/direct-debit/mandates/{self.mandate_uid}", self._sandbox),
            headers=self._auth_headers,
        )
        response.raise_for_status()
        response = response.json()

        self.reference = response.get("reference")
        self.status = response.get("status")
        self.source = response.get("source")
        self.created = response.get("created")
        self.cancelled = response.get("cancelled")
        self.next_date = response.get("nextDate")
        self.last_date = response.get("lastDate")
        self.originator_name = response.get("originatorName")
        self.originator_uid = response.get("originatorUid")
        self.merchant_uid = response.get("merchantUid")
        self.category_uid = response.get("categoryUid")

        last_payment = response.get("lastPayment")

        if not last_payment:
            return

        self.last_payment_date = last_payment.get("lastDate")

        last_amount = last_payment.get("lastAmount")
        self.last_payment_currency = last_amount.get("currency")
        self.last_payment_minor_units = last_amount.get("minorUnits")
