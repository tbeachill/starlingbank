from requests import get
from typing import Dict
from typing import List
from .saving_space import SavingSpace
from .spending_space import SpendingSpace
from .spending_insights import SpendingInsights
from .direct_debit import DirectDebit
from .standing_order import StandingOrder
from .card import Card
from .address import Address
from .constants import *
from .utils import _url
from base64 import b64decode
from datetime import datetime

class StarlingAccount:
    """Representation of a Starling Account."""
    
    def __init__(
        self, api_token: str, update: bool = False, sandbox: bool = False
    ) -> None:
        """Call to initialise a StarlingAccount object."""
        self._api_token = api_token
        self._sandbox = sandbox
        self._auth_headers = {
            "Authorization": "Bearer {0}".format(self._api_token),
            "Content-Type": "application/json",
        }
        self.account_type = None
        self.account_name = None
        self.default_category = None
        self.currency = None
        self.created_at = None
        
        self._set_basic_account_data()

        # Account Data
        self.account_identifier = None
        self.bank_identifier = None
        self.iban = None
        self.bic = None
        
        # Account Holder Data
        self.account_holder_uid = None
        self.account_holder_type = None
        
        # Individual Data
        self.title = None
        self.first_name = None
        self.last_name = None
        self.date_of_birth = None
        self.email = None
        self.phone = None
        
        # Address Data
        self.current_address = None
        self.previous_addresses = [] # type: List[Address]
        
        self.cards = {}  # type: Dict[str, Card]

        # Balance Data
        self.cleared_balance = None
        self.effective_balance = None
        self.pending_transactions = None
        self.accepted_overdraft = None
        
        # Spaces Data
        self.spending_spaces = {}  # type: Dict[str, SpendingSpace]
        self.saving_spaces = {}   # type: Dict[str, SavingSpace]
        
        # Spending Insights
        self.spending_insights = {}  # type: Dict[str, SpendingInsights]
        
        self.direct_debits = {}  # type: Dict[str, DirectDebit]
        
        self.standing_orders = {}  # type: Dict[str, StandingOrder]
        
        if update:
            self.update_account_data()
            self.update_balance_data()
            self.update_spaces_data()
            self.update_insights_data()
            self.update_direct_debit_data()
            self.update_individual_data()
            self.update_address_data()

    def update_account_data(self) -> None:
        """Get basic information for the account."""
        response = get(
            _url(
                "/accounts/{0}/identifiers".format(self._account_uid),
                self._sandbox,
            ),
            headers=self._auth_headers,
        )
        response.raise_for_status()
        response = response.json()

        self.account_identifier = response.get("accountIdentifier")
        self.bank_identifier = response.get("bankIdentifier")
        self.iban = response.get("iban")
        self.bic = response.get("bic")
        
        self._update_account_info()
        
    def _update_account_info(self) -> None:
        """Get the account information."""
        response = get(
            _url("/accounts/", self._sandbox),
            headers=self._auth_headers,
        )
        response.raise_for_status()
        response = response.json()
        
        accounts = response.get("accounts")[0]
        self.default_category = accounts.get("defaultCategory")
        self.created_at = accounts.get("createdAt")
        self.account_type = accounts.get("accountType")
        self.account_name = accounts.get("name")
        self.currency = accounts.get("currency")
        
    def update_account_holder_data(self) -> None:
        """Get account holder information for the account."""
        response = get(
            _url("/account-holder", self._sandbox),
            headers=self._auth_headers,
        )
        response.raise_for_status()
        response = response.json()

        self.account_holder_uid = response.get("accountHolderUid")
        self.account_holder_type = response.get("accountHolderType")
        
    def update_individual_data(self) -> None:
        """Get individual information for the account."""
        response = get(
            _url("/account-holder/individual", self._sandbox),
            headers=self._auth_headers,
        )
        response.raise_for_status()
        response = response.json()

        self.title = response.get("title")
        self.first_name = response.get("firstName")
        self.last_name = response.get("lastName")
        self.date_of_birth = response.get("dateOfBirth")
        self.email = response.get("email")
        self.phone = response.get("phone")
        
    def update_address_data(self) -> None:
        """Get address information for the account."""
        response = get(
            _url("/addresses", self._sandbox),
            headers=self._auth_headers,
        )
        response.raise_for_status()
        response = response.json()

        current = response.get("current")
        self.current_address = Address(
            self._auth_headers, self._sandbox, self._account_uid,
            current.get("line1"), current.get("line2"), current.get("line3"),
            current.get("postTown"), current.get("postCode"),
            current.get("countryCode")
        )
        
        self.previous_addresses = []
        
        for previous in response.get("previous", []):
            self.previous_addresses.append(
                Address(
                    self._auth_headers, self._sandbox, self._account_uid,
                    previous.get("line1"), previous.get("line2"),
                    previous.get("line3"), previous.get("postTown"),
                    previous.get("postCode"), previous.get("countryCode")
                )
            )

    def update_card_data(self) -> None:
        """Get the card information for the account."""
        response = get(
            _url("/cards", self._sandbox), headers=self._auth_headers
        )
        response.raise_for_status()
        response = response.json()
        
        for card in response.get("cards", []):
            card_uid = card.get("cardUid")
            self.cards[card_uid] = Card(
                self._auth_headers, self._sandbox, self._account_uid, card_uid
            )
            self.cards[card_uid].update()
    
    def update_balance_data(self) -> None:
        """Get the latest balance information for the account."""
        response = get(
            _url(
                "/accounts/{0}/balance".format(self._account_uid),
                self._sandbox,
            ),
            headers=self._auth_headers,
        )
        response.raise_for_status()

        response = response.json()
        self.cleared_balance = response["clearedBalance"]["minorUnits"]
        self.effective_balance = response["effectiveBalance"]["minorUnits"]
        self.pending_transactions = response["pendingTransactions"][
            "minorUnits"
        ]
        self.accepted_overdraft = response["acceptedOverdraft"]["minorUnits"]

    def update_insights_data(self, year=None) -> None:
        """Get spending insights for each month of the specified year,
        or the current year if not specified."""
        
        query_year = datetime.now().year if year is None else year
        end_month = 12 if query_year < datetime.now().year else datetime.now().month
        for month in range(1, end_month + 1):
            self.spending_insights[month] = SpendingInsights(
                self._auth_headers, self._sandbox, self._account_uid,
                month, query_year
            )
            self.spending_insights[month].update_insights()
            
    def update_direct_debit_data(self) -> None:
        """Get the Direct Debit mandates for the account."""
        response = get(
            _url(
                "/direct-debit/mandates".format(self._account_uid),
                self._sandbox,
            ),
            headers=self._auth_headers,
        )
        response.raise_for_status()
        response = response.json()
        
        for mandate in response.get("mandates", []):
            uid = mandate.get("uid")
            self.direct_debits[uid] = DirectDebit(
                self._auth_headers, self._sandbox, self._account_uid,
                uid
            )
            self.direct_debits[uid].update_insights()
            
    def update_standing_order_data(self) -> None:
        """Get the Standing Orders for the account."""
        print(self.default_category)
        response = get(
            _url(
                "/payments/local/account/{0}/category/{1}/standing-orders".format(
                    self._account_uid, self.default_category
                ),
                self._sandbox,
            ),
            headers=self._auth_headers,
        )
        response.raise_for_status()
        response = response.json()
        
        for order in response.get("standingOrders", []):
            payment_order_uid = order.get("paymentOrderUid")
            self.standing_orders[payment_order_uid] = StandingOrder(
                self._auth_headers, self._sandbox, self._account_uid,
                payment_order_uid, self.default_category
            )
            self.standing_orders[payment_order_uid].update_insights()
            
        self.update_spaces_data()
        
        for space_uid in self.spending_spaces.keys():
            self._get_space_standing_orders(space_uid)
            
    def _get_space_standing_orders(self, space_uid: str) -> None:
        """Get the Standing Orders for a specific space."""
        response = get(
            _url(
                "/payments/local/account/{0}/category/{1}/standing-orders".format(
                    self._account_uid, space_uid
                ),
                self._sandbox,
            ),
            headers=self._auth_headers,
        )
        response.raise_for_status()
        response = response.json()
        
        for order in response.get("standingOrders", []):
            payment_order_uid = order.get("paymentOrderUid")
            self.standing_orders[payment_order_uid] = StandingOrder(
                self._auth_headers, self._sandbox, self._account_uid,
                payment_order_uid, space_uid
            )
            self.standing_orders[payment_order_uid].update_insights()
    
    def update_spaces_data(self) -> None:
        """Get the latest Spaces information for the account."""
        response = get(
            _url(
                "/account/{0}/spaces".format(self._account_uid),
                self._sandbox,
            ),
            headers=self._auth_headers,
        )
        response.raise_for_status()
        response = response.json()
        self._update_spending_spaces(response)
        self._update_saving_spaces(response)
        
    def _update_spending_spaces(self, response) -> None:
        response_spending_spaces = response.get("spendingSpaces", {})
        returned_uids = []

        # New / update
        for space in response_spending_spaces:
            uid = space.get("spaceUid")
            returned_uids.append(uid)

            # Intiialise new SpendingSpace object if new
            if uid not in self.spending_spaces:
                self.spending_spaces[uid] = SpendingSpace(
                    self._auth_headers, self._sandbox, self._account_uid
                )

            self.spending_spaces[uid].update(space)

        # Forget about Spending Spaces if the UID isn't returned by Starling
        for uid in list(self.spending_spaces):
            if uid not in returned_uids:
                self.spending_spaces.pop(uid)
    
    def _update_saving_spaces(self, response) -> None:
        response_saving_spaces = response.get("savingsGoals", {})
        returned_uids = []
        
        # New / update
        for space in response_saving_spaces:
            uid = space.get("savingsGoalUid")
            returned_uids.append(uid)

            # Intiialise new SavingSpace object if new
            if uid not in self.saving_spaces:
                self.saving_spaces[uid] = SavingSpace(
                    self._auth_headers, self._sandbox, self._account_uid
                )

            self.saving_spaces[uid].update(space)

        # Forget about Saving Spaces if the UID isn't returned by Starling
        for uid in list(self.saving_spaces):
            if uid not in returned_uids:
                self.saving_spaces.pop(uid)

    def _set_basic_account_data(self):
        response = get(
            _url("/accounts", self._sandbox), headers=self._auth_headers
        )
        response.raise_for_status()
        response = response.json()

        # Assume there will be only 1 account as this is the case with
        # personal access.
        account = response["accounts"][0]
        self._account_uid = account["accountUid"]
        self.currency = account["currency"]
        self.created_at = account["createdAt"]
        self._update_account_info()

    def get_profile_image(self, filename: str = None) -> None:
        """Download the profile image associated with an account holder."""
        if filename is None:
            filename = "{0}.png".format(self.name)

        endpoint = "/account-holder/{0}/profile-image".format(
            self.account_holder_uid
        )

        response = get(
            _url(endpoint, self._sandbox), headers=self._auth_headers
        )
        response.raise_for_status()

        base64_image = response.json()["base64EncodedPhoto"]
        with open(filename, "wb") as file:
            file.write(b64decode(base64_image))
