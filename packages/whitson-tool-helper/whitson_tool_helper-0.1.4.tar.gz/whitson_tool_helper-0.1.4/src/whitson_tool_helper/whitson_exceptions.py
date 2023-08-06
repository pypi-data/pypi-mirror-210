from typing import List


class WhitsonException(Exception):
    pass


class CalculationTimeoutError(WhitsonException):
    def __str__(self) -> str:
        return "Calculation timed out. Please contact the support team."


class MissingCredentialsError(WhitsonException):
    def __init__(self, credential_type: str) -> None:
        self.credential_type = credential_type

    def __str__(self) -> str:
        return f"Credentials of {self.credential_type} are missing."


class MissingEnvironmentVariableError(WhitsonException):
    def __init__(self, vars: List[str]):
        self.vars = vars

    def __str__(self) -> str:
        return "Missing environment variables: " + ", ".join(self.vars)
