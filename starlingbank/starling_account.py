from requests import get
from typing import Dict
from .saving_space import SavingSpace
from .spending_space import SpendingSpace
from .constants import *
from .utils import _url
from base64 import b64decode

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
        self._set_basic_account_data()

        # Account Data
        self.account_identifier = None
        self.bank_identifier = None
        self.iban = None
        self.bic = None
        
        # Account Holder
        self.account_holder_name = None
        self.account_holder_uid = None
        self.account_holder_type = None

        # Balance Data
        self.cleared_balance = None
        self.effective_balance = None
        self.pending_transactions = None
        self.accepted_overdraft = None
        
        # Spaces Data
        self.spending_spaces = {}  # type: Dict[str, SpendingSpace]
        self.saving_spaces = {}   # type: Dict[str, SavingSpace]
        
        if update:
            self.update_account_data()
            self.update_balance_data()
            self.update_spaces_data()

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
        self._update_account_holder_name()
        
    def _update_account_holder_name(self) -> None:
        """Get account holder name for the account."""
        response = get(
            _url("/account-holder/name", self._sandbox),
            headers=self._auth_headers,
        )
        response.raise_for_status()
        response = response.json()

        self.account_holder_name = response.get("accountHolderName")

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
