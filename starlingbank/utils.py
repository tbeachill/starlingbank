from .constants import *

def _url(endpoint: str, sandbox: bool = False) -> str:
    """Build a URL from the API's base URLs."""
    if sandbox is True:
        url = BASE_URL_SANDBOX
    else:
        url = BASE_URL
    return "{0}{1}".format(url, endpoint)
