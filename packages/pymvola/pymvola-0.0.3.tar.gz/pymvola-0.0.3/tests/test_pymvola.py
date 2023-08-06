# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring


import os

from dotenv import load_dotenv
from pymvola import PyMVola
from pymvola.util import Env
from pymvola.models import Transaction, Debitor, Creditor
from pymvola.exceptions import MVolaResponseException

load_dotenv()

# Test will fail if you don't provide a valid consumer_key and consumer_secret.
CONSUMER_KEY = os.environ.get("PYMVOLA_CONSUMER_KEY")
CONSUMER_SECRET = os.environ.get("PYMVOLA_CONSUMER_SECRET")


def test_pymvola_get_token():
    api = PyMVola(
        CONSUMER_KEY,
        CONSUMER_SECRET,
        {
            "env": Env.PREPROD,
            "user_msisdn_account_identifier": "0343500003",
            "partner_name": "BluelineTest,",
        },
    )

    token = api.get_token()
    assert isinstance(token, str)


def test_pymolva_get_token_invalid_auth():
    api = PyMVola(
        "wrong_login",
        "wrong_passwd",
        {
            "env": Env.PREPROD,
            "user_msisdn_account_identifier": "0343500003",
            "partner_name": "BluelineTest,",
        },
    )

    try:
        api.get_token()
    except Exception as err:  # pylint: disable=broad-exception-caught
        assert isinstance(err, MVolaResponseException)
        return
    assert False


def test_pymvola_init_transaction():
    api = PyMVola(
        CONSUMER_KEY,
        CONSUMER_SECRET,
        {
            "env": Env.PREPROD,
            "user_msisdn_account_identifier": "0343500003",
            "partner_name": "BluelineTest,",
        },
    )

    transaction = Transaction(
        1000,
        "Payement Marchant",
        "0343500003",
        "0343500004",
    )

    transaction = api.init_transaction(transaction)
    assert isinstance(transaction, Transaction)


def test_pymvola_get_transaction_status():
    api = PyMVola(
        CONSUMER_KEY,
        CONSUMER_SECRET,
        {
            "env": Env.PREPROD,
            "user_msisdn_account_identifier": "0343500003",
            "partner_name": "BluelineTest,",
        },
    )

    transaction = Transaction(
        1000,
        "Payement Marchant",
        "0343500003",
        "0343500004",
    )
    try:
        transaction = api.init_transaction(transaction)
        transaction_status = api.get_transaction_status(
            transaction.original_transaction_reference
        )
    except Exception:  # pylint: disable=:broad-exception-caught
        assert False

    assert transaction_status == Transaction.Status.PENDING
