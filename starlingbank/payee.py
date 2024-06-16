from typing import List, Dict
from base64 import b64decode
from datetime import datetime, timedelta
from requests import get
from .utils import _url
from .constants import GET_TIMEOUT


class Payee:
    """Representation of a payee.

    Required Scopes:
        `payee:read`
        `scheduled-payment:read`
        `payee-transaction:read`
        `payee-image:read`

    Args:
        auth_headers (dict of {str, str}): Starling API authentication headers.
        sandbox (bool): True if sandbox mode, False otherwise.
        account_uid (str): Account UID.
        payee_uid (str): Payee UID.
    """

    def __init__(
        self, auth_headers: Dict, sandbox: bool, account_uid: str, payee_uid: str
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
        self.payee_accounts = {}  # type: Dict[str, PayeeAccount]

    def update(self) -> None:
        """Update payee.

        Required Scopes:
            `payee:read`
            `scheduled-payment:read`
            `payee-transaction:read`
        """
        response = get(
            _url("/payees", self._sandbox),
            headers=self._auth_headers,
            timeout=GET_TIMEOUT,
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
                        self._auth_headers,
                        self._sandbox,
                        self._account_uid,
                        payee_account_uid,
                        self.uid,
                    )
                    self.payee_accounts[payee_account_uid].update(response)
                return

    def get_payee_image(self, filename: str = None) -> str:
        """Get the payee image.

        Required Scopes:
            `payee-image:read`

        Args:
            filename (str): Filename to save the image to.
        """
        if filename is None:
            filename = f"{self.uid}.png"

        response = get(
            _url(f"/payees/{self.uid}/image", self._sandbox),
            headers=self._auth_headers,
            timeout=GET_TIMEOUT,
        )
        response.raise_for_status()

        base64_image = response.json()["base64EncodedPhoto"]
        with open(filename, "wb") as file:
            file.write(b64decode(base64_image))


class PayeeAccount:
    """Representation of a payee account.

    Args:
        auth_headers (dict of {str, str}): Starling API authentication headers.
        sandbox (bool): True if sandbox mode, False otherwise.
        account_uid (str): Account UID.
        payee_account_uid (str): Payee Account UID.
        payee_uid (str): Payee UID.
        payments_since (str): Payments since date.
    """

    def __init__(
        self,
        auth_headers: Dict,
        sandbox: bool,
        account_uid: str,
        payee_account_uid: str,
        payee_uid: str,
        payments_since: str = None,
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
        self.last_references = []  # type: List[str]

        # Payment Data
        self.payments = {}  # type: Dict[str, PayeePayment]
        self.payments_since = payments_since
        self.scheduled_payments = {}  # type: Dict[str, PayeeScheduledPayment]

    def update(self, response: str) -> None:
        """Update the payee account.

        Required Scopes:
            `payee:read`

        Args:
            response (str): Response from the Starling API.
        """
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
                        self._update_payee_scheduled_payments()
                        return

    def _update_payee_payments(self) -> None:
        """Get payee payments.

        Required Scopes:
            `payee-transaction:read`
        """
        if self.payments_since is None:
            since_date = datetime.now() - timedelta(days=365)
            self.payments_since = since_date.strftime("%Y-%m-%d")

        response = get(
            _url(
                f"/payees/{self.payee_uid}/account/{self.account_uid}/payments?since={self.payments_since}",
                self._sandbox,
            ),
            headers=self._auth_headers,
            timeout=GET_TIMEOUT,
        )
        response.raise_for_status()
        response = response.json()

        for payment in response.get("payments", []):
            payment_uid = payment.get("paymentUid")
            self.payments[payment_uid] = PayeePayment(
                self._auth_headers,
                self._sandbox,
                self._account_uid,
                self.payee_uid,
                payment_uid,
                self.account_uid,
            )
            self.payments[payment_uid].update(response)

    def _update_payee_scheduled_payments(self) -> None:
        """Get payee scheduled payments.

        Required Scopes:
            `scheduled-payment:read`
        """
        response = get(
            _url(
                f"/payees/{self.payee_uid}/account/{self.account_uid}/scheduled-payments",
                self._sandbox,
            ),
            headers=self._auth_headers,
            timeout=GET_TIMEOUT,
        )
        response.raise_for_status()
        response = response.json()

        for payment in response.get("scheduledPayments", []):
            payment_uid = payment.get("paymentOrderUid")
            self.scheduled_payments[payment_uid] = PayeeScheduledPayment(
                self._auth_headers,
                self._sandbox,
                self._account_uid,
                self.payee_uid,
                payment_uid,
                self.account_uid,
            )
            self.scheduled_payments[payment_uid].update(response)


class PayeePayment:
    """Representation of a payee payment.

    Args:
        auth_headers (dict of {str, str}): Starling API authentication headers.
        sandbox (bool): True if sandbox mode, False otherwise.
        account_uid (str): Account UID.
        payee_uid (str): Payee UID.
        payment_uid (str): Payment UID.
        payee_account_uid (str): Payee Account UID.
    """

    def __init__(
        self,
        auth_headers: Dict,
        sandbox: bool,
        account_uid: str,
        payee_uid: str,
        payment_uid: str,
        payee_account_uid: str,
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

    def update(self, response: str) -> None:
        """Update payee payment.

        Required Scopes:
            `payee-transaction:read`

        Args:
            response (str): Response from the Starling API.
        """
        for payment in response.get("payments", []):
            if payment.get("paymentUid") == self.payment_uid:
                self.reference = payment.get("reference")
                self.created_at = payment.get("createdAt")
                self.spending_category = payment.get("spendingCategory")

                payment_amount = payment.get("paymentAmount")
                self.currency = payment_amount.get("currency")
                self.minor_units = payment_amount.get("minorUnits")
                return


class PayeeScheduledPayment:
    """Representation of a payee scheduled payment.

    Args:
        auth_headers (dict of {str, str}): Starling API authentication headers.
        sandbox (bool): True if sandbox mode, False otherwise.
        account_uid (str): Account UID.
        payee_uid (str): Payee UID.
        payment_uid (str): Payment UID.
        payee_account_uid (str): Payee Account UID.
    """

    def __init__(
        self,
        auth_headers: Dict,
        sandbox: bool,
        account_uid: str,
        payee_uid: str,
        payment_uid: str,
        payee_account_uid: str,
    ) -> None:
        self._auth_headers = auth_headers
        self._sandbox = sandbox
        self._account_uid = account_uid

        # Payee Payment Data
        self.payee_uid = payee_uid
        self.payment_order_uid = payment_uid
        self.payee_account_uid = payee_account_uid

        self.account_holder_uid = None
        self.category_uid = None
        self.reference = None
        self.start_date = None
        self.next_date = None
        self.end_date = None
        self.payment_type = None
        self.spending_category = None

        self.next_payment_currency = None
        self.next_payment_minor_units = None

        self.recurrence_start_date = None
        self.recurrence_frequency = None
        self.recurrence_interval = None
        self.recurrence_count = None
        self.recurrence_until_date = None
        self.recurrence_week_start = None
        self.recurrence_days = []  # type: List[str]
        self.recurrence_month_day = None
        self.recurrence_month_week = None

    def update(self, response: str) -> None:
        """Update payee scheduled payment.

        Required Scopes:
            `scheduled-payment:read`

        Args:
            response (str): Response from the Starling API.
        """
        for payment in response.get("scheduledPayments", []):
            if payment.get("paymentOrderUid") == self.payment_order_uid:
                self.account_holder_uid = payment.get("accountHolderUid")
                self.category_uid = payment.get("categoryUid")
                self.reference = payment.get("reference")
                self.start_date = payment.get("startDate")
                self.next_date = payment.get("nextDate")
                self.end_date = payment.get("endDate")
                self.payment_type = payment.get("paymentType")
                self.spending_category = payment.get("spendingCategory")

                next_payment = payment.get("nextPaymentAmount")
                self.next_payment_currency = next_payment.get("currency")
                self.next_payment_minor_units = next_payment.get("minorUnits")

                recurrence = payment.get("recurrenceRule")
                self.recurrence_start_date = recurrence.get("startDate")
                self.recurrence_frequency = recurrence.get("frequency")
                self.recurrence_interval = recurrence.get("interval")
                self.recurrence_count = recurrence.get("count")
                self.recurrence_until_date = recurrence.get("untilDate")
                self.recurrence_week_start = recurrence.get("weekStart")
                self.recurrence_days = recurrence.get("days", [])
                self.recurrence_month_day = recurrence.get("monthDay")
                self.recurrence_month_week = recurrence.get("monthWeek")
                return
