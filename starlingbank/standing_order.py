from requests import get
from typing import Dict
from .constants import *
from .utils import _url

class StandingOrder:
    """Representation of a standing order."""
    
    def __init__(
        self, auth_headers: Dict, sandbox: bool, account_uid: str,
        payment_order_uid: str, category_uid: str
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
        
        self.standing_order_recurrence = None
        self.start_date = None
        self.frequency = None
        self.interval = None
        self.count = None
        
        self.next_date = None
        self.updated_at = None
        self.spending_category = None
        
    def update_insights(self) -> None:
        """Update standing order."""
        response = get(
            _url("/payments/local/account/{0}/category/{1}/standing-orders/{2}".format(
                self._account_uid, self.category_uid, self.payment_order_uid), 
                self._sandbox),
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
