from typing import Dict
from requests import get
from .utils import _url
from .constants import GET_TIMEOUT


class StandingOrder:
    """Representation of a standing order.

    Required Scopes:
        `standing-order:read`
        `standing-order-own:read`

    Args:
        auth_headers (dict of {str, str}): Starling API authentication headers.
        sandbox (bool): True if sandbox mode, False otherwise.
        account_uid (str): Account UID.
        payment_order_uid (str): Payment order UID.
        category_uid (str): Category UID.
    """

    def __init__(
        self,
        auth_headers: Dict,
        sandbox: bool,
        account_uid: str,
        payment_order_uid: str,
        category_uid: str,
    ) -> None:
        self._auth_headers = auth_headers
        self._sandbox = sandbox
        self._account_uid = account_uid

        self.category_uid = category_uid
        self.payment_order_uid = payment_order_uid

        self.currency = None
        self.minor_units = None

        self.reference = None
        self.payee_uid = None
        self.payee_account_uid = None

        self.start_date = None
        self.frequency = None
        self.interval = None
        self.count = None
        self.until_date = None

        self.next_date = None
        self.cancelled_at = None
        self.updated_at = None
        self.spending_category = None

    def update(self) -> None:
        """Update standing order.

        Required Scopes:
            `standing-order:read`
            `standing-order-own:read`
        """
        response = get(
            _url(
                f"/payments/local/account/{self._account_uid}/category/{self.category_uid}/standing-orders/{self.payment_order_uid}",
                self._sandbox,
            ),
            headers=self._auth_headers,
            timeout=GET_TIMEOUT,
        )
        response.raise_for_status()
        response = response.json()

        self.category_uid = response.get("categoryUid")
        self.payment_order_uid = response.get("paymentOrderUid")
        self.reference = response.get("reference")
        self.payee_uid = response.get("payeeUid")
        self.payee_account_uid = response.get("payeeAccountUid")
        self.next_date = response.get("nextDate")
        self.cancelled_at = response.get("cancelledAt")
        self.updated_at = response.get("updatedAt")
        self.spending_category = response.get("spendingCategory")

        amount = response.get("amount", {})
        self.currency = amount.get("currency")
        self.minor_units = amount.get("minorUnits")

        recurrence = response.get("standingOrderRecurrence", {})
        self.start_date = recurrence.get("startDate")
        self.frequency = recurrence.get("frequency")
        self.interval = recurrence.get("interval")
        self.count = recurrence.get("count")
        self.until_date = recurrence.get("untilDate")
