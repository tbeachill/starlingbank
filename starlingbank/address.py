from typing import Dict


class Address:
    """Representation of an address.

    Required Scopes:
        `address:read`

    Args:
        auth_headers (dict of {str, str}): Starling API authentication headers.
        sandbox (bool): Whether or not to use the sandbox environment.
        account_uid (str): Account UID.
        line1 (str): First line of the address.
        line2 (str): Second line of the address.
        line3 (str): Third line of the address.
        town (str): Town of the address.
        postcode (str): Postcode of the address.
        country (str): Country code of the address.
    """

    __slots__ = [
        "_auth_headers",
        "_sandbox",
        "_account_uid",
        "line1",
        "line2",
        "line3",
        "post_town",
        "postcode",
        "country",
    ]

    def __init__(
        self,
        auth_headers: Dict,
        sandbox: bool,
        account_uid: str,
        line1: str,
        line2: str,
        line3: str,
        town: str,
        postcode: str,
        country: str,
    ) -> None:
        self._auth_headers = auth_headers
        self._sandbox = sandbox
        self._account_uid = account_uid

        # Address Data
        self.line1 = line1
        self.line2 = line2
        self.line3 = line3
        self.post_town = town
        self.postcode = postcode
        self.country = country
