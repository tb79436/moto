"""Exceptions raised by the lakeformation service."""
from moto.core.exceptions import JsonRESTError


class LakeFormationClientError(JsonRESTError):
    code = 400


class InvalidParameterException(LakeFormationClientError):
    def __init__(self, msg=None, constraint=None, parameter=None, value=None):
        self.code = 400
        if constraint:
            msg = f"1 validation error detected: Value '{value}' at '{parameter}' failed to satisfy constraint: {constraint}"
        super().__init__(
            "InvalidParameterException", msg or "A parameter is specified incorrectly."
        )
