from requests import get
from typing import Dict
from .constants import *
from .utils import _url
from calendar import month_name

class SpendingInsights:
    """Representation of spending insights for a specific month."""
    
    def __init__(
        self, auth_headers: Dict, sandbox: bool, account_uid: str,
        month: str, year: str
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
        self.spending_categories = {} # type: Dict[str, Dict[str, str]]
        self.counter_parties = {} # type: Dict[str, Dict[str, str]]
        
    def update(self) -> None:
        """Update all spending insights."""
        self._update_spending_categories()
        self._update_counter_parties()
            
    def _update_spending_categories(self) -> None:
        """Get spending insights by category."""
        response = get(
            _url("/accounts/{0}/spending-insights/spending-category?month={1}&year={2}".format(
                self._account_uid, self.month, self.year), self._sandbox),
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
                "transactionCount": category.get("transactionCount")
            }
            
    def _update_counter_parties(self) -> None:
        """Get spending insights by counter party."""
        response = get(
            _url(
                "/accounts/{0}/spending-insights/counter-party?month={1}&year={2}".format(
                self._account_uid, self.month, self.year), self._sandbox),
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
                "transactionCount": party.get("transactionCount")
            }
