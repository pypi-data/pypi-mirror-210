"""
This module provides all enumeration used inside the PyMVola API.

This itend to make configuration of PyMVola API more consise and easier.

NB:
    - Any modification of this module should be repercuted in pymvola.util.__init__ file
    
Author: Ryuka (lovanirina.ran@gmail.com)
Date: 15/05/2023
"""

from enum import Enum


class UserLanguage(str, Enum):
    """User language used for the MVola API."""

    FR = "FR"


class Currency(str, Enum):
    """Currency used for the transaction."""

    AR = "Ar"


class Env(str, Enum):
    """MVola environment used for the API.

    Attributes:
        PREPROD: environment used for the SANDBOX.
        PROD: environment used for real API.
    """

    PREPROD = "preprod"
    PROD = "prod"
