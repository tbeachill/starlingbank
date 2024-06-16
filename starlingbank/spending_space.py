from base64 import b64decode
from typing import Dict
from requests import get
from .utils import _url


class SpendingSpace:
    """Representation of a Spending Space.

    Required Scopes:
        `space:read`

    Args:
        auth_headers (dict of {str, str}): Starling API authentication headers.
        sandbox (bool): True if sandbox mode, False otherwise.
        account_uid (str): Account UID.
    """

    def __init__(self, auth_headers: Dict, sandbox: bool, account_uid: str) -> None:
        self._auth_headers = auth_headers
        self._sandbox = sandbox
        self._account_uid = account_uid

        self.uid = None
        self.name = None
        self.balance_currency = None
        self.balance_minor_units = None
        self.card_association_uid = None
        self.sort_order = None
        self.spending_space_type = None
        self.state = None

    def update(self, space: Dict = None) -> None:
        """Update a single Spending Space.

        Required Scopes:
            `space:read`
        """
        if space is None:
            endpoint = f"/account/{self._account_uid}/spaces/spending/{self.uid}"
            response = get(_url(endpoint, self._sandbox), headers=self._auth_headers)
            response.raise_for_status()
            space = response.json()

        self.uid = space.get("spaceUid")
        self.name = space.get("name")

        balance = space.get("balance", {})
        self.balance_currency = balance.get("currency")
        self.balance_minor_units = balance.get("minorUnits")

        self.card_association_uid = space.get("cardAssociationUid")
        self.sort_order = space.get("sortOrder")
        self.state = space.get("spendingSpaceType")
        self.state = space.get("state")

    def get_image(self, filename: str = None) -> None:
        """Download the photo associated with a Spending Space.

        Required Scopes:
            `space:read`

        Args:
            filename (str): Filename to save the image to.
        """
        if filename is None:
            filename = f"{self.uid}.png"

        endpoint = f"/account/{self._account_uid}/spaces/{self.uid}/photo"

        response = get(_url(endpoint, self._sandbox), headers=self._auth_headers)
        response.raise_for_status()

        base64_image = response.json()["base64EncodedPhoto"]
        with open(filename, "wb") as file:
            file.write(b64decode(base64_image))
