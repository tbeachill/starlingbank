from .constants import BASE_URL, BASE_URL_SANDBOX


def _url(endpoint: str, sandbox: bool = False) -> str:
    """Build a URL from the API's base URLs.

    Args:
        endpoint (str): API endpoint URL.
        sandbox (bool): True if sandbox mode, False otherwise.
    """
    if sandbox is True:
        url = BASE_URL_SANDBOX
    else:
        url = BASE_URL
    return f"{url}{endpoint}"
