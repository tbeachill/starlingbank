from typing import Dict
from typing import List
from base64 import b64decode
from datetime import datetime
from requests import get
from .address import Address
from .card import Card
from .direct_debit import DirectDebit
from .payee import Payee
from .round_up import RoundUp
from .savings_goal import SavingsGoal
from .spending_insights import SpendingInsights
from .spending_space import SpendingSpace
from .standing_order import StandingOrder
from .utils import _url


class StarlingAccount:
    """Representation of a Starling Account.

    Args:
        api_token (str): Starling API token.
        update (bool): True to update all data on initialisation, False otherwise.
        sandbox (bool): True if sandbox mode, False otherwise.
    """

    def __init__(
        self, api_token: str, update: bool = False, sandbox: bool = False
    ) -> None:
        """Call to initialise a StarlingAccount object."""
        self._api_token = api_token
        self._sandbox = sandbox
        self._auth_headers = {
            "Authorization": f"Bearer {self._api_token}",
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
        self.previous_addresses = []  # type: List[Address]

        # Settle Up Data
        self.settle_up_status = None
        self.settle_up_link = None

        self.cards = {}  # type: Dict[str, Card]

        self.payees = {}  # type: Dict[str, Payee]

        self.round_up = None

        # Balance Data
        self.cleared_balance = None
        self.effective_balance = None
        self.pending_transactions = None
        self.accepted_overdraft = None
        self.total_cleared_balance = None
        self.total_effective_balance = None

        # Spaces Data
        self.spending_spaces = {}  # type: Dict[str, SpendingSpace]
        self.savings_goals = {}  # type: Dict[str, SavingsGoal]

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
            self.update_standing_order_data()
            self.update_individual_data()
            self.update_address_data()
            self.update_card_data()
            self.update_settle_up_data()
            self.update_payee_data()
            self.update_round_up_data()

    def update_account_data(self) -> None:
        """Get basic information for the account.

        Required Scopes:
            `account-identifier:read`
            `account:read`
            `account-list:read`
        """
        response = get(
            _url(
                f"/accounts/{self._account_uid}/identifiers",
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
        """Get the account information.

        Required Scopes:
            `account:read`
            `account-list:read`
        """
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
        """Get account holder information for the account.

        Required Scopes:
            `customer:read`
            `account-holder-type:read`
        """
        response = get(
            _url("/account-holder", self._sandbox),
            headers=self._auth_headers,
        )
        response.raise_for_status()
        response = response.json()

        self.account_holder_uid = response.get("accountHolderUid")
        self.account_holder_type = response.get("accountHolderType")

    def update_individual_data(self) -> None:
        """Get individual information for the account.

        Required Scopes:
            `customer:read`
        """
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
        """Get address information for the account.

        Required Scopes:
            `address:read`
        """
        response = get(
            _url("/addresses", self._sandbox),
            headers=self._auth_headers,
        )
        response.raise_for_status()
        response = response.json()

        current = response.get("current")
        self.current_address = Address(
            self._auth_headers,
            self._sandbox,
            self._account_uid,
            current.get("line1"),
            current.get("line2"),
            current.get("line3"),
            current.get("postTown"),
            current.get("postCode"),
            current.get("countryCode"),
        )

        self.previous_addresses = []

        for previous in response.get("previous", []):
            self.previous_addresses.append(
                Address(
                    self._auth_headers,
                    self._sandbox,
                    self._account_uid,
                    previous.get("line1"),
                    previous.get("line2"),
                    previous.get("line3"),
                    previous.get("postTown"),
                    previous.get("postCode"),
                    previous.get("countryCode"),
                )
            )

    def update_card_data(self) -> None:
        """Get the card information for the account.

        Required Scopes:
            `card:read`
        """
        response = get(_url("/cards", self._sandbox), headers=self._auth_headers)
        response.raise_for_status()
        response = response.json()

        for card in response.get("cards", []):
            card_uid = card.get("cardUid")
            self.cards[card_uid] = Card(
                self._auth_headers, self._sandbox, self._account_uid, card_uid
            )
            self.cards[card_uid].update()

    def update_round_up_data(self) -> None:
        """Get the round up information for the account.

        Required Scopes:
            `savings-goal:read`
        """
        self.round_up = RoundUp(self._auth_headers, self._sandbox, self._account_uid)
        self.round_up.update()

    def update_settle_up_data(self) -> None:
        """Get the settle up information for the account.

        Required Scopes:
            `settle-up:read`
        """
        response = get(
            _url("/settle-up/profile", self._sandbox), headers=self._auth_headers
        )
        response.raise_for_status()
        response = response.json()

        self.settle_up_status = response.get("status")
        self.settle_up_link = response.get("settleUpLink")

    def update_payee_data(self) -> None:
        """Get the payee information for the account.

        Required Scopes:
            `payee:read`
            `scheduled-payment:read`
            `payee-transaction:read`
        """
        response = get(_url("/payees", self._sandbox), headers=self._auth_headers)
        response.raise_for_status()
        response = response.json()

        for payee in response.get("payees", []):
            payee_uid = payee.get("payeeUid")
            self.payees[payee_uid] = Payee(
                self._auth_headers, self._sandbox, self._account_uid, payee_uid
            )
            self.payees[payee_uid].update()

    def update_balance_data(self) -> None:
        """Get the latest balance information for the account.

        Required Scopes:
            `balance:read`
        """
        response = get(
            _url(
                f"/accounts/{self._account_uid}/balance",
                self._sandbox,
            ),
            headers=self._auth_headers,
        )
        response.raise_for_status()

        response = response.json()
        self.cleared_balance = response["clearedBalance"]["minorUnits"]
        self.effective_balance = response["effectiveBalance"]["minorUnits"]
        self.pending_transactions = response["pendingTransactions"]["minorUnits"]
        self.accepted_overdraft = response["acceptedOverdraft"]["minorUnits"]
        self.total_cleared_balance = response["totalClearedBalance"]["minorUnits"]
        self.total_effective_balance = response["totalEffectiveBalance"]["minorUnits"]

    def update_insights_data(self, year: str = None) -> None:
        """Get spending insights for each month of the specified year,
        or the current year if not specified.

        Required Scopes:
            `transaction:read`

        Args:
            year (str): The year to get spending insights for.
        """

        query_year = datetime.now().year if year is None else year
        end_month = 12 if query_year < datetime.now().year else datetime.now().month
        for month in range(1, end_month + 1):
            self.spending_insights[month] = SpendingInsights(
                self._auth_headers, self._sandbox, self._account_uid, month, query_year
            )
            self.spending_insights[month].update()

    def update_direct_debit_data(self) -> None:
        """Get the Direct Debit mandates for the account.

        Required Scopes:
            `mandate:read`
        """
        response = get(
            _url(
                "/direct-debit/mandates",
                self._sandbox,
            ),
            headers=self._auth_headers,
        )
        response.raise_for_status()
        response = response.json()

        for mandate in response.get("mandates", []):
            uid = mandate.get("uid")
            self.direct_debits[uid] = DirectDebit(
                self._auth_headers, self._sandbox, self._account_uid, uid
            )
            self.direct_debits[uid].update()

    def update_standing_order_data(self) -> None:
        """Get the Standing Orders for the account.

        Required Scopes:
            `standing-order:read`
            `standing-order-own:read`
        """
        response = get(
            _url(
                f"/payments/local/account/{self._account_uid}/category/{self.default_category}/standing-orders",
                self._sandbox,
            ),
            headers=self._auth_headers,
        )
        response.raise_for_status()
        response = response.json()

        for order in response.get("standingOrders", []):
            payment_order_uid = order.get("paymentOrderUid")
            self.standing_orders[payment_order_uid] = StandingOrder(
                self._auth_headers,
                self._sandbox,
                self._account_uid,
                payment_order_uid,
                self.default_category,
            )
            self.standing_orders[payment_order_uid].update()

        self.update_spaces_data()

        for space_uid in self.spending_spaces:
            self._get_space_standing_orders(space_uid)

    def _get_space_standing_orders(self, space_uid: str) -> None:
        """Get the Standing Orders for a specific space.

        Required Scopes:
            `standing-order:read`
            `standing-order-own:read`

        Args:
            space_uid (str): The UID of the space to get the Standing Orders for.
        """
        response = get(
            _url(
                f"/payments/local/account/{self._account_uid}/category/{space_uid}/standing-orders",
                self._sandbox,
            ),
            headers=self._auth_headers,
        )
        response.raise_for_status()
        response = response.json()

        for order in response.get("standingOrders", []):
            payment_order_uid = order.get("paymentOrderUid")
            self.standing_orders[payment_order_uid] = StandingOrder(
                self._auth_headers,
                self._sandbox,
                self._account_uid,
                payment_order_uid,
                space_uid,
            )
            self.standing_orders[payment_order_uid].update()

    def update_spaces_data(self) -> None:
        """Get the latest Spaces information for the account.

        Required Scopes:
            `space:read`
            `savings-goal:read`
            `savings-goal-transfer:read`
        """
        response = get(
            _url(
                f"/account/{self._account_uid}/spaces",
                self._sandbox,
            ),
            headers=self._auth_headers,
        )
        response.raise_for_status()
        response = response.json()
        self._update_spending_spaces(response)
        self._update_savings_goals(response)

    def _update_spending_spaces(self, response: str) -> None:
        """Update the Spending Spaces for the account.

        Required Scopes:
            `space:read`

        Args:
            response (str): JSON response from Starling API.
        """
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

    def _update_savings_goals(self, response: str) -> None:
        """Update the Savings Goals for the account.

        Required Scopes:
            `savings-goal:read`
            `savings-goal-transfer:read`

        Args:
            response (str): JSON response from Starling API.
        """
        response_savings_goals = response.get("savingsGoals", {})
        returned_uids = []

        # New / update
        for goal in response_savings_goals:
            uid = goal.get("savingsGoalUid")
            returned_uids.append(uid)

            # Intiialise new SavingsGoal object if new
            if uid not in self.savings_goals:
                self.savings_goals[uid] = SavingsGoal(
                    self._auth_headers, self._sandbox, self._account_uid
                )

            self.savings_goals[uid].update(goal)

        # Forget about Savings Goals if the UID isn't returned by Starling
        for uid in list(self.savings_goals):
            if uid not in returned_uids:
                self.savings_goals.pop(uid)

    def _set_basic_account_data(self):
        """Set the basic account data for the account.

        Required Scopes:
            `account:read`
            `account-list:read`
        """
        response = get(_url("/accounts", self._sandbox), headers=self._auth_headers)
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
        """Download the profile image associated with an account holder.

        Required Scopes:
            `profile-image:read`

        Args:
            filename (str): Filename to save the image to.
        """
        if filename is None:
            filename = f"{self.account_holder_uid}.png"

        endpoint = f"/account-holder/{self.account_holder_uid}/profile-image"

        response = get(_url(endpoint, self._sandbox), headers=self._auth_headers)
        response.raise_for_status()

        base64_image = response.json()["base64EncodedPhoto"]
        with open(filename, "wb") as file:
            file.write(b64decode(base64_image))
