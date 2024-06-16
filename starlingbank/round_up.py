from typing import Dict
from requests import get
from .utils import _url


class RoundUp:
    """Representation of a round up.

    Required Scopes:
        `savings-goal:read`

    Args:
        auth_headers (dict of {str, str}): Starling API authentication headers.
        sandbox (bool): True if sandbox mode, False otherwise.
        account_uid (str): Account UID.
    """

    def __init__(self, auth_headers: Dict, sandbox: bool, account_uid: str) -> None:
        self._auth_headers = auth_headers
        self._sandbox = sandbox
        self._account_uid = account_uid

        self.active = None
        self.primary_category_uid = None
        self.goal_uid = None
        self.multiplier = None
        self.activated_at = None
        self.activated_by = None

        self.update()

    def update(self) -> None:
        """Update round up.

        Required Scopes:
            `savings-goal:read`
        """
        response = get(
            _url(f"/feed/account/{self._account_uid}/round-up", self._sandbox),
            headers=self._auth_headers,
        )
        response.raise_for_status()
        response = response.json()

        self.active = response.get("active")

        if self.active is False:
            return

        round_up_details = response.get("roundUpGoalDetails")
        self.primary_category_uid = round_up_details.get("primaryCategoryUid")
        self.goal_uid = round_up_details.get("roundUpGoalUid")
        self.multiplier = round_up_details.get("roundUpMultiplier")
        self.activated_at = round_up_details.get("activatedAt")
        self.activated_by = round_up_details.get("activatedBy")
