"""
This module provides a core class for using the PyMVola API.

Author: Ryuka (lovanirina.ran@gmail.com)
Date: 14/05/2023
"""

import json

import requests
from pymvola.util import Env, get_uuid
from pymvola.util.consts import (
    MVOLA_URL_PREPROD,
    MVOLA_URL_PROD,
    DEFAULT_TIMEOUT,
    MVOLA_URL_TRANSACTION_BASE,
)
from pymvola.util.enumeration import UserLanguage
from pymvola.util.authorization import basic_authorization, bearer_authorization
from pymvola.exceptions import GenericException, MVolaResponseException
from pymvola.models import Transaction, Msisdn


class PyMVola:
    """Core class to use the PyMVola API."""

    def __init__(
        self, consumer_key: str, consumer_secret: str, conf: dict = None
    ) -> None:
        """Initialize a new instance of the PyMVola class.

        `consumer_key` and `consumer_secret` is given when you subscribe to an application.
        For a full reference watch the MVola API documentation: https://www.mvola.mg/devportal/

        Args:
            consumer_key (str): The consumer key for accessing the MVola API.
            consumer_secret (str): The consumer secret for accessing the MVola API.
            conf (dict): Configuration dictionnary used to overide the default configuration.

                ```python
                self.conf = {
                    "env": Env.PREPROD,
                    "timeout": DEFAULT_TIMEOUT,
                    "partner_name": "CHANGE_ME",
                    "user_language": UserLanguage.FR,
                    "user_msisdn_account_identifier": "CHANGE_ME",
                }
                ```
        """
        #
        # set-up configuration
        #
        self.conf = {
            "env": Env.PREPROD,
            "timeout": DEFAULT_TIMEOUT,
            "partner_name": "CHANGE_ME",
            "user_language": UserLanguage.FR,
            "user_msisdn_account_identifier": "CHANGE_ME",
        }
        self._update_conf(conf)

        #
        # set-up consumer information
        #
        self._consumer_key = consumer_key
        self._consumer_secret = consumer_secret

    def _get_user_account_identifier(self):
        user_msisdn_account_identifier = Msisdn(
            self.conf["user_msisdn_account_identifier"]
        )
        return f"msisdn;{user_msisdn_account_identifier}"

    @property
    def url(self):
        """Get the URL of the current environment

        Returns:
            str: URL of the current environment
        """
        return MVOLA_URL_PROD if (self.conf["env"] == Env.PROD) else MVOLA_URL_PREPROD

    def _update_conf(self, conf: dict) -> None:
        self.conf.update(conf)

    def get_token(self) -> str:
        """Get Token to use for authentication for other functionnality of MVola API.

        Raises:
            GenericException: Raised when the specific cause of exception is not handled.

        Return:
            str: Token string that correspond to the <consumer_key> and the <consumer_secret>.
        """
        url = f"{self.url}/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Cache-Control": "no-cache",
            "Authorization": basic_authorization(
                self._consumer_key, self._consumer_secret
            ),
        }
        payload = "grant_type=client_credentials&scope=EXT_INT_MVOLA_SCOPE"

        try:
            response = requests.request(
                "POST", url, headers=headers, data=payload, timeout=self.conf["timeout"]
            )
        except Exception as err:
            raise GenericException(err) from err

        response_json = response.json()

        if response.ok:
            return response_json["access_token"]

        raise MVolaResponseException(response)

    def init_transaction(self, transaction: Transaction):
        """Init a transaction.

        Args:
            transaction (Transaction): Instance of Transaction

        Raises:
            MVolaResponseException: When response is K.O

        Returns:
            Transaction: instance of Transaction but with original transaction id and new status.
        """
        url = f"{self.url}{MVOLA_URL_TRANSACTION_BASE}/"

        payload = json.dumps(transaction.to_schema(self.conf["partner_name"]))

        headers = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
            "Version": "1.0",
            "X-CorrelationID": get_uuid(),
            "UserLanguage": self.conf["user_language"],
            "UserAccountIdentifier": self._get_user_account_identifier(),
            "Authorization": bearer_authorization(self.get_token()),
        }

        response = requests.request(
            "POST", url, headers=headers, data=payload, timeout=self.conf["timeout"]
        )

        response_json = response.json()

        if response.ok:
            transaction.original_transaction_reference = response_json[
                "serverCorrelationId"
            ]
            transaction.status = Transaction.Status.INITIED
            return transaction

        raise MVolaResponseException(response)

    def get_transaction_status(self, transaction_id: str):
        """Get the status of a transaction.

        Args:
            transaction_id (str): transaction id provided by MVola

        Raises:
            MVolaResponseException: When response is K.O

        Returns:
            str: status of the given transaction id
        """
        url = f"{self.url}{MVOLA_URL_TRANSACTION_BASE}/status/{transaction_id}"

        payload = {}

        headers = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
            "Version": "1.0",
            "X-CorrelationID": get_uuid(),
            "UserLanguage": self.conf["user_language"],
            "UserAccountIdentifier": self._get_user_account_identifier(),
            "partnerName": "TestBlueline",
            "Authorization": bearer_authorization(self.get_token()),
        }

        response = requests.request(
            "GET", url, headers=headers, data=payload, timeout=self.conf["timeout"]
        )

        response_json = response.json()

        if response.ok:
            return response_json["status"]

        raise MVolaResponseException(response)
