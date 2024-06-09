from typing import Dict
from .constants import *
from .utils import _url
from requests import get

class Card:
    """Representation of a card."""
        
    def __init__(
        self, auth_headers: Dict, sandbox: bool, account_uid: str,
        card_uid: str
    ) -> None:
        self._auth_headers = auth_headers       
        self._sandbox = sandbox
        self._account_uid = account_uid

        # Card Data
        self.card_uid = card_uid
        self.public_token = None
        self.enabled = None
        self.wallet_notification_enabled = None
        self.pos_enabled = None
        self.atm_enabled = None
        self.online_enabled = None
        self.mobile_wallet_enabled = None
        self.gambling_enabled = None
        self.mag_stripe_enabled = None
        self.cancelled = None
        self.activation_requested = None
        self.activated = None
        self.end_of_card_number = None
        self.currency_flags_enabled = None
        self.currency_flags = {} # type: Dict[str, str]
        
    def update(self) -> None:
        """Update card."""
        response = get(
            _url("/cards".format(), self._sandbox),
            headers=self._auth_headers
        )
        response.raise_for_status()
        response = response.json()
        
        for card in response.get("cards", []):
            if card.get("cardUid") == self.card_uid:
                self.public_token = card.get("publicToken")
                self.enabled = card.get("enabled")
                self.wallet_notification_enabled = card.get("walletNotificationEnabled")
                self.pos_enabled = card.get("posEnabled")
                self.atm_enabled = card.get("atmEnabled")
                self.online_enabled = card.get("onlineEnabled")
                self.mobile_wallet_enabled = card.get("mobileWalletEnabled")
                self.gambling_enabled = card.get("gamblingEnabled")
                self.mag_stripe_enabled = card.get("magStripeEnabled")
                self.cancelled = card.get("cancelled")
                self.activation_requested = card.get("activationRequested")
                self.activated = card.get("activated")
                self.end_of_card_number = card.get("endOfCardNumber")
                self.card_association_uid = card.get("cardAssociationUid")
                
                for currency in card.get("currencyFlags", []):
                    self.currency_flags[currency.get("currency")] = currency.get("enabled")
                return
