"""
This module provides all models class used inside the PyMVola API.

Author: Ryuka (lovanirina.ran@gmail.com)
Date: 15/05/2023
"""

import re

from pymvola.exceptions import InvalidMsisdn
from pymvola.util.consts import (
    GENERIC_PHONE_NUMBER_PATTERN,
    TELMA_PHONE_NUMBER_PATTERN,
    MINIMAL_MSISDN_LEN,
)
from pymvola.util.enumeration import Currency
from pymvola.util import get_uuid, now


class Msisdn:
    """Msisdn Class"""

    def __init__(self, msisdn) -> None:
        self.value = self.regularize_msisdn(msisdn)
        self.check_validity_of_msisdn(self.value)

    @classmethod
    def check_validity_of_msisdn(cls, msisdn: str) -> None:
        """Check the validity of a given msisdn

        Args:
            msisdn (str): Msisdn to check validity of.

        Raises:
            InvalidMsisdn: When the msisdn don't correspond to the minimal len\
                or don't match the generic pattern.
        """
        if bool(re.match(GENERIC_PHONE_NUMBER_PATTERN, msisdn)):
            return
        raise InvalidMsisdn(msisdn)

    @classmethod
    def regularize_msisdn(cls, msisdn: str) -> str:
        """Regularize msisdn to match the MVola API restriction.

        Args:
            msisdn (str): msisdn to regularize

        Raises:
            InvalidMsisdn: raise when msisdn don't have minimal msisdn len.

        Returns:
            str: regularized msisdn.
        """
        if len(msisdn) < MINIMAL_MSISDN_LEN:
            raise InvalidMsisdn(msisdn)
        result = msisdn[-9::]
        result = f"0{result}"
        return result

    def __str__(self) -> str:
        return self.value


class Debitor(Msisdn):
    """Msisdn that correspond to the DebitParty."""


class Creditor(Msisdn):
    """Msisdn that correspond to the CreditParty."""

    @classmethod
    def check_validity_of_msisdn(cls, msisdn: str) -> None:
        """Check the validity of a given msisdn

        Args:
            msisdn (str): Msisdn to check validity of.

        Raises:
            InvalidMsisdn: When the msisdn don't correspond to the minimal len\
                or don't match the telma phone pattern.
        """
        super().check_validity_of_msisdn(msisdn)
        if bool(re.match(TELMA_PHONE_NUMBER_PATTERN, msisdn)):
            return
        raise InvalidMsisdn(msisdn)


class Transaction:
    """Represent a transaction."""

    class Status:
        """Represent the different status of a Transaction."""

        NOT_INITIED = "not_initied"
        INITIED = "initied"
        PENDING = "pending"
        FAILED = "failed"
        COMPLETED = "completed"

    def __init__(
        self,
        amount: float,
        description_text: str,
        creditor: object,
        debitor: object,
        requesting_organisation_transaction_reference: str = None,
        **kwargs,
    ) -> None:
        # amount
        self.amount = str(amount)

        # currency
        if kwargs.get("currency") is None:
            self.currency = Currency.AR
        else:
            self.currency = kwargs.get("currency")

        # descriptionText
        self.description_text = description_text

        # requestingOrganisationTransactionReference
        if requesting_organisation_transaction_reference:
            self.requesting_organisation_transaction_reference = (
                requesting_organisation_transaction_reference
            )
        else:
            self.requesting_organisation_transaction_reference = get_uuid()

        # requestDate
        self.request_date = now()

        # originalTransactionReference
        if kwargs.get("original_transaction_reference") is None:
            self.original_transaction_reference = ""
        else:
            self.original_transaction_reference = kwargs.get(
                "original_transaction_reference"
            )

        # debitParty
        self.debitor = Debitor(debitor)
        self.debit_party = [{"key": "msisdn", "value": f"{self.debitor}"}]

        # creditParty
        self.creditor = Creditor(creditor)
        self.credit_party = [{"key": "msisdn", "value": f"{self.creditor}"}]

        # status
        self.status = self.Status.NOT_INITIED

    def to_schema(self, partner_name) -> dict:
        """Create a dict from the transaction that will be used to sent as data to MVola API."""
        return {
            "amount": self.amount,
            "currency": self.currency,
            "descriptionText": self.description_text,
            "requestingOrganisationTransactionReference": (
                self.requesting_organisation_transaction_reference
            ),
            "requestDate": self.request_date,
            "originalTransactionReference": "",
            "debitParty": self.debit_party,
            "creditParty": self.credit_party,
            "metadata": [
                {"key": "partnerName", "value": partner_name},
                {"key": "fc", "value": "USD"},
                {"key": "amountFc", "value": "1"},
            ],
        }
