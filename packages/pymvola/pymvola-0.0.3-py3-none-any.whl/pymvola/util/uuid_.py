"""
This module provides all functionnality used to create unique uid to PyMVola API.

NB:
    - Any modification of this module should be repercuted in pymvola.util.__init__ file

Author: Ryuka (lovanirina.ran@gmail.com)
Date: 15/05/2023
"""

import uuid


def get_uuid():
    """Create a uuid.

    Returns:
        str: uuid generated.
    """
    return str(uuid.uuid4())
