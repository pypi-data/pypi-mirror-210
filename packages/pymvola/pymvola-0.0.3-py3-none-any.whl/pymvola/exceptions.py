"""
This module provides all exception class used inside the PyMVola API.

Author: Ryuka (lovanirina.ran@gmail.com)
Date: 15/05/2023
"""


class GenericException(Exception):
    """Generic Exception for PyMVola API.

    This happen when the exception cause is not handled correctly.
    """


class InvalidMsisdn(Exception):
    """Invalid msisdn."""


class MVolaResponseException(Exception):
    """MVola Response Exception"""

    def __init__(self, response) -> None:
        self._response = response
        self.status_code = response.status_code
        self.reason = response.reason
        self.text = response.text

        self.error = None
        self.error_code = None
        self.error_description = None
        self.error_datetime = None
        self.error_parameters = None

        payload = response.json()

        if payload.get("fault"):
            self.error = payload["fault"]["message"]
            self.error_description = payload["fault"]["description"]
        elif payload.get("errorCategory"):
            self.error = payload["errorCategory"]
            self.error_code = payload["errorCode"]
            self.error_description = payload["errorDescription"]
            self.error_datetime = payload["errorDateTime"]
            self.error_parameters = payload["errorParameters"]
        elif payload.get("error"):
            self.error = payload["error"]
            self.error_description = payload["error_description"]

        super().__init__(
            f"Mvola API Response :: {self.status_code} {self.reason} "
            f":: {self.error} - {self.error_description}"
        )
