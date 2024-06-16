from typing import Dict
from calendar import month_name
from requests import get
from .utils import _url


class SpendingInsights:
    """Representation of spending insights for a specific month.

    Required Scopes:
        `transaction:read`

    Args:
        auth_headers (dict of {str, str}): Starling API authentication headers.
        sandbox (bool): True if sandbox mode, False otherwise.
        account_uid (str): Account UID.
        month (str): Month in format "MM".
        year (str): Year in format "YYYY".
    """

    def __init__(
        self, auth_headers: Dict, sandbox: bool, account_uid: str, month: str, year: str
    ) -> None:
        self._auth_headers = auth_headers
        self._sandbox = sandbox
        self._account_uid = account_uid
        self.year = year
        self.month = month_name[month].upper()

        # Overall Data
        self.period = None
        self.total_spent = None
        self.total_received = None
        self.net_spend = None

        # Breakdown Data
        self.spending_categories = {}  # type: Dict[str, Dict[str, str]]
        self.counter_parties = {}  # type: Dict[str, Dict[str, str]]

    def update(self) -> None:
        """Update all spending insights.

        Required Scopes:
            `transaction:read`
        """
        self._update_spending_categories()
        self._update_counter_parties()

    def _update_spending_categories(self) -> None:
        """Get spending insights by category.

        Required Scopes:
            `transaction:read`
        """
        response = get(
            _url(
                f"/accounts/{self._account_uid}/spending-insights/spending-category?month={self.month}&year={self.year}",
                self._sandbox,
            ),
            headers=self._auth_headers,
        )
        response.raise_for_status()
        response = response.json()

        self.period = response.get("period")
        self.total_spent = response.get("totalSpent")
        self.total_received = response.get("totalReceived")
        self.net_spend = response.get("netSpend")

        for category in response.get("breakdown"):
            self.spending_categories[category.get("spendingCategory")] = {
                "totalSpent": category.get("totalSpent"),
                "totalReceived": category.get("totalReceived"),
                "netSpend": category.get("netSpend"),
                "netDirection": category.get("netDirection"),
                "currency": category.get("currency"),
                "percentage": category.get("percentage"),
                "transactionCount": category.get("transactionCount"),
            }

    def _update_counter_parties(self) -> None:
        """Get spending insights by counter party.

        Required Scopes:
            `transaction:read`
        """
        response = get(
            _url(
                f"/accounts/{self._account_uid}/spending-insights/counter-party?month={self.month}&year={self.year}",
                self._sandbox,
            ),
            headers=self._auth_headers,
        )
        response.raise_for_status()
        response = response.json()

        for party in response.get("breakdown"):
            self.counter_parties[party.get("counterPartyName")] = {
                "counterPartyUid": party.get("counterPartyUid"),
                "counterPartyType": party.get("counterPartyType"),
                "counterPartyName": party.get("counterPartyName"),
                "totalSpent": party.get("totalSpent"),
                "totalReceived": party.get("totalReceived"),
                "netSpend": party.get("netSpend"),
                "netDirection": party.get("netDirection"),
                "currency": party.get("currency"),
                "percentage": party.get("percentage"),
                "transactionCount": party.get("transactionCount"),
            }
