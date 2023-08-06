"""
This module provides all functionnality used for authorization to PyMVola API.

Author: Ryuka (lovanirina.ran@gmail.com)
Date: 15/05/2023
"""

import base64


def basic_authorization(login: str, passwd: str) -> str:
    """Create a base64 encoded string that correspond to <username>:<password> for basic auth.

    Args:
        login (str): Login used for authorization
        passwd (str): Password used for authorization

    Returns:
        str: base64 encoded string that correspond to <username>:<password> for basic auth.
    """
    encoded_credentials = base64.b64encode(f"{login}:{passwd}".encode())
    encoded_credentials_as_str = encoded_credentials.decode()
    return f"Basic {encoded_credentials_as_str}"


def bearer_authorization(token: str) -> str:
    """Create a bearer authorization string.

    Args:
        token (str): token used to create the bearer authorization.

    Returns:
        str: bearer authorization
    """
    return f"Bearer {token}"
