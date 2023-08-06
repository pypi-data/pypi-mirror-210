# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring

from pymvola.models import Msisdn, Debitor, Creditor
from pymvola.exceptions import InvalidMsisdn


def test_regularize_msisdn():
    raw_msisdn_list = [
        "+261361122233",
        "0361122233",
        "361122233",
    ]
    for raw_msisdn in raw_msisdn_list:
        assert "0361122233" == Msisdn.regularize_msisdn(raw_msisdn)


def test_check_validity_msisdn():
    valid_msisdn = [
        "0361122233",
        "0381122233",
        "0341122233",
        "0331122233",
        "0321122233",
    ]
    invalid_msisdn = [
        "+261361122233",
        "+261381122233",
        "+261341122233",
        "+261331122233",
        "+261321122233",
        "1234567890",
        "12345",
    ]

    for msisdn in valid_msisdn:
        try:
            Msisdn.check_validity_of_msisdn(msisdn)
        except InvalidMsisdn:
            assert False

    # Test invalid msisdn
    for msisdn in invalid_msisdn:
        try:
            Msisdn.check_validity_of_msisdn(msisdn)
            assert False  # Exception should have been raised
        except InvalidMsisdn:
            assert True


def test_debitor_check_validity_msisdn():
    valid_msisdn = [
        "+261381122233",
        "+261341122233",
        "+261331122233",
        "+261321122233",
    ]
    invalid_msisdn = [
        "1234567890",
        "12345",
    ]

    for msisdn in valid_msisdn:
        try:
            Debitor(msisdn)
        except InvalidMsisdn:
            assert False

    # Test invalid debitor msisdn
    for msisdn in invalid_msisdn:
        try:
            Debitor(msisdn)
            assert False  # Exception should have been raised
        except InvalidMsisdn:
            assert True


def test_creditor_check_validity_msisdn():
    valid_msisdn = [
        "+261381122233",
        "+261341122233",
    ]
    invalid_msisdn = [
        "+261331122233",
        "+261321122233",
        "1234567890",
        "12345",
    ]

    for msisdn in valid_msisdn:
        try:
            Creditor(msisdn)
        except InvalidMsisdn:
            assert False

    # Test invalid creditor msisdn
    for msisdn in invalid_msisdn:
        try:
            Creditor(msisdn)
            assert False  # Exception should have been raised
        except InvalidMsisdn:
            assert True
