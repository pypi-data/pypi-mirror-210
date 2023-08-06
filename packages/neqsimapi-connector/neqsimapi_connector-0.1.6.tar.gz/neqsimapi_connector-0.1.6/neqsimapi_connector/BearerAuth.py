import os
import sys
from typing import List

import msal
import requests
from msal_extensions import (FilePersistence,
                             FilePersistenceWithDataProtection,
                             KeychainPersistence, PersistedTokenCache)


def get_login_name() -> str:
    """Get login name

    Returns:
        str: name of logged in user
    """
    env_names = ["LOGNAME", "USER", "LNAME", "USERNAME"]
    for name in env_names:
        if os.getenv(name) is not None:
            return os.getenv(name)


def get_app_with_cache(client_id: str, authority: str, token_location: str = "", verbose: bool = False) -> msal.PublicClientApplication:
    """Get msal application with cached token if available.

    Args:
        client_id (str): Azure Client ID to request token from.
        authority (str): Authority to authenticate against.
        token_location (str, optional): Location of token persistance file. Defaults to "" giving "neqsimapi_token_cache.bin" in current folder.
        verbose (bool, optional): Set true to write debug information. Defaults to False.

    Returns:
        msal.PublicClientApplication: Application object to authenticate with.
    """
    if token_location is None or len(token_location) == 0:
        token_location = "neqsimapi_token_cache.bin"

    if sys.platform.startswith('win'):
        persistence = FilePersistenceWithDataProtection(token_location)
    elif sys.platform.startswith('darwin'):
        persistence = KeychainPersistence(
            token_location, "my_service_name", "my_account_name")
    else:
        persistence = FilePersistence(token_location)

    if verbose:
        print("Is this MSAL persistence cache encrypted?",
              persistence.is_encrypted)
        
    cache = PersistedTokenCache(persistence)
    return msal.PublicClientApplication(
        client_id=client_id, authority=authority, token_cache=cache)


class BearerAuth(requests.auth.AuthBase):
    """Class for getting bearer token authentication using msal.

    Get BearerAuth object by calling get_bearer_token.
    """

    def __init__(self, token) -> None:
        self.token = token

    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r

    @staticmethod
    def get_bearer_token_auth(tenantID: str, clientID: str, scopes: List[str], username: str = f"{get_login_name()}@equinor.com", verbose: bool = False):
        """Get BearerAuth object with access token for an azure application.

        Args:
            tenantID (str): Azure tenant ID.
            clientID (str): Azure Client ID to request token from.
            scopes (List[str]): Scopes to request token for.
            username (str, optional): User name to get token for. Defaults to f"{get_login_name()}@equinor.com".
            verbose (bool, optional): Set true to print debug messages. Defaults to False.

        Raises:
            Exception: If authentication fails.

        Returns:
            BearerAuth: Authorization object with bearer token.
        """

        authority = f"https://login.microsoftonline.com/{tenantID}"
        result = None

        # Try to get Access Token silently from cache
        app = get_app_with_cache(
            client_id=clientID, authority=authority, token_location="", verbose=verbose)
        accounts = app.get_accounts(username=username)
        if accounts:
            if verbose:
                print(
                    f"Found account in token cache: {username}")
                print("Attempting to obtain a new Access Token using the Refresh Token")
            result = app.acquire_token_silent_with_error(
                scopes=scopes, account=accounts[0])

        if result is None or (isinstance(result, dict) and "error_codes" in result.keys() and 50173 in result['error_codes']):
            # Try to get a new Access Token using the Interactive Flow
            if verbose:
                print(
                    "Interactive Authentication required to obtain a new Access Token.")
            result = app.acquire_token_interactive(
                scopes=scopes, domain_hint=tenantID)

        if result and isinstance(result, dict) and "access_token" in result.keys() and result["access_token"]:
            if verbose:
                print("Success")
            return BearerAuth(result["access_token"])
        else:
            if verbose:
                print("Failed")
            raise Exception("Failed authenticating")
