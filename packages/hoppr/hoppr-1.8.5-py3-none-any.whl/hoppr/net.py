"""
Hoppr Network utility functions
"""
import requests

from requests.auth import HTTPBasicAuth

from hoppr.exceptions import HopprLoadDataError
from hoppr.models.credentials import CredentialRequiredService, Credentials
from hoppr.utils import load_string


def load_url(url: str):
    """
    Load config content (either json or yml) from a url into a dict
    """
    creds = Credentials.find(url)

    response = None
    if creds is not None:
        authorization_headers = {
            "PRIVATE-TOKEN": creds.password.get_secret_value(),
            "Authorization": f"Bearer {creds.password.get_secret_value()}",
        }

        basic_auth = HTTPBasicAuth(username=creds.username, password=creds.password.get_secret_value())
        response = requests.get(url, auth=basic_auth, headers=authorization_headers, timeout=60)
    else:
        response = requests.get(url, timeout=60)

    response.raise_for_status()
    valid_data = True
    try:
        if isinstance(response.content, bytes):
            return load_string(response.content.decode("utf-8"))
        if isinstance(response.content, str):
            return load_string(response.content)
        valid_data = False
    except HopprLoadDataError as parse_error:
        message = f"Unable to parse result from {url}."
        if response.url != url:
            message += f" Request was redirected to {response.url}. An auth issue might have occurred."
        raise HopprLoadDataError(message) from parse_error

    if not valid_data:
        raise HopprLoadDataError("Response type is not bytes or str")

    return None  # pragma: no cover


def download_file(url: str, dest: str, creds: CredentialRequiredService | None = None):
    """
    Download content from a url into a file
    """
    if creds is None:
        creds = Credentials.find(url)

    basic_auth = None
    if creds is not None:
        basic_auth = HTTPBasicAuth(username=creds.username, password=creds.password.get_secret_value())

    response = requests.get(url, auth=basic_auth, allow_redirects=True, stream=True, verify=True, timeout=60)

    if 200 <= response.status_code < 300:
        with open(dest, "wb") as out_file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    out_file.write(chunk)

    return response
