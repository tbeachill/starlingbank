from typing import Dict
from .constants import *
from .utils import _url
from requests import get

class RoundUp:
    """Representation of a round up."""
        
    def __init__(
        self, auth_headers: Dict, sandbox: bool, account_uid: str
    ) -> None:
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
        """Update round up."""
        response = get(
            _url("/feed/account/{0}/round-up".format(
                self._account_uid), self._sandbox),
            headers=self._auth_headers
        )
        response.raise_for_status()
        response = response.json()
        
        self.active = response.get("active")
        
        if self.active == False:
            return
        
        round_up_details = response.get("roundUpGoalDetails")
        self.primary_category_uid = round_up_details.get("primaryCategoryUid")
        self.goal_uid = round_up_details.get("roundUpGoalUid")
        self.multiplier = round_up_details.get("roundUpMultiplier")
        self.activated_at = round_up_details.get("activatedAt")
        self.activated_by = round_up_details.get("activatedBy")
