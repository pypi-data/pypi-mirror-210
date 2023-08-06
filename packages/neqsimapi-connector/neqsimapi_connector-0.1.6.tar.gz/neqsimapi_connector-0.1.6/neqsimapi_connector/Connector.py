from urllib.parse import urljoin

import requests

from neqsimapi_connector.BearerAuth import BearerAuth


def get_url_NeqSimAPI(use_test: bool = False) -> str:
    """Get base url to NeqSimAPI.

    Args:
        use_test (bool, optional): Set true to get url to test environment. Defaults to False.

    Returns:
        str: Base url to NeqSimAPI.
    """
    if use_test:
        return "https://api-neqsimapi-dev.radix.equinor.com"
    else:
        return "https://neqsimapi.app.radix.equinor.com"


def get_auth_NeqSimAPI() -> BearerAuth:
    """Get authentication object containing bearer token.

    Returns:
        BearerAuth: Authentication object for use with request session.
    """
    tenantID = "3aa4a235-b6e2-48d5-9195-7fcf05b459b0"
    client_id = "dde32392-142b-4933-bd87-ecdd28d7250f"
    scope = ["api://dde32392-142b-4933-bd87-ecdd28d7250f/Calculate.All"]

    return BearerAuth.get_bearer_token_auth(tenantID=tenantID, clientID=client_id, scopes=scope)


class Connector():
    """Class for getting data from NeqSimAPI restful api.
    """

    def __init__(
        self,
        url: str = "",
        auth=None,
        verifySSL: bool = False,
    ):
        if url is None or len(url) == 0:
            self.base_url = get_url_NeqSimAPI()
        else:
            self.base_url = url

        if auth is None:
            auth = get_auth_NeqSimAPI()
        self.session = requests.Session()
        self.session.auth = auth
        if verifySSL is False:
            requests.packages.urllib3.disable_warnings(
                requests.packages.urllib3.exceptions.InsecureRequestWarning
            )
        self.session.verify = verifySSL

    def get_results(self, calculation_id: str, a_sync: bool = True) -> dict:
        """Get results from async calculation with calculation id.

        Args:
            calculation_id (str): Calculation id. Returned when starting calculation with post or post_async.
            a_sync (bool, optional): Set False to loop internally while waiting for a reply from the calculation. Defaults to True.

        Returns:
            dict: Results when finished or dictionary with status.
        """
        url = urljoin(self.base_url, f"results/{calculation_id}")
        res = self.session.get(url)

        res = res.json()

        if a_sync:
            return res
        else:
            while isinstance(res, dict) and 'status' in res.keys() and res['status'] == 'working':
                res = self.get_results(calculation_id=calculation_id)

            if isinstance(res, dict) and 'result' in res.keys():
                res = res['result']

            return res

    def post(self, url: str, data: dict) -> dict:
        """Start calculation and get results or status dict from api.

        Args:
            url (str): Full or partial url to end point.
            data (dict): Data to pass to calculation.

        Returns:
            dict: Result or status dict from end point.
        """

        if self.base_url not in url:
            url = urljoin(self.base_url, url)
        res = self.session.post(url, json=data)

        res.raise_for_status()

        return res.json()

    def post_async(self, url: str, data: dict) -> dict:
        """Start async calculation and get status result.
        NB! Results must be gotten with get_results()

        Args:
            url (str): Full or partial url to end point.
            data (dict): Data to pass to calculation.

        Returns:
            dict: Status dict or None if endpoint is not async. 
        """
        if self.base_url not in url:
            url = urljoin(self.base_url, url)
        res = self.session.post(url, json=data)

        res.raise_for_status()

        if isinstance(res.json(), dict) and 'id' in res.json().keys():
            id = res.json()
            status = id['status']
            id = id['id']
            return id, status

        return None
