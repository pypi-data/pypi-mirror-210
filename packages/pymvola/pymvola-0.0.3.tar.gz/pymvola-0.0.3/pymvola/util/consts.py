"""
This module provides all constants used alongside the PyMVola API.

Author: Ryuka (lovanirina.ran@gmail.com)
Date: 14/05/2023
"""

MVOLA_URL_PREPROD = "https://devapi.mvola.mg"
MVOLA_URL_PROD = "https://api.mvola.mg"

MVOLA_URL_TRANSACTION_BASE = "/mvola/mm/transactions/type/merchantpay/1.0.0"

GENERIC_PHONE_NUMBER_PATTERN = r"^(03)\d{8}$"
TELMA_PHONE_NUMBER_PATTERN = r"^(034|038)\d{7}$"

MINIMAL_MSISDN_LEN = 9
"""ex: 3xxxxxxxx."""

DEFAULT_TIMEOUT = 10
