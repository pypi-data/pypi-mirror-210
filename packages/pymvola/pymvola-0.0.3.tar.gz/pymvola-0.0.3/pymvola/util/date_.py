"""
This module provides all date utility used inside the PyMVola API.

NB:
    - Any modification of this module should be repercuted in pymvola.util.__init__ file

Author: Ryuka (lovanirina.ran@gmail.com)
Date: 19/05/2023
"""

from datetime import datetime


def now() -> str:
    """Get MVola formatted style of now.


    Returns:
        str: MVola formatted date style of current time.
    """
    return f_date_mvola_api(datetime.now())


def f_date_mvola_api(date_time: datetime) -> str:
    """Format a given datetime to a MVola style.

    Args:
        datetime (datetime): Python datetime to format.

    Returns:
        str: Formated python datetime accepted by MVola API.
    """
    date_format = "%Y-%m-%dT%H:%M:%S.%fZ"

    #
    # For MVolaAPI
    #
    # We use `2023-05-13T11:24:10.093Z`
    # Instead of : `2023-05-13T11:24:10.093180Z`
    date_str = date_time.strftime(date_format)
    date_str = date_str[:-4] + "Z"

    return date_str
