from dataclasses import dataclass


@dataclass
class OutputData:
    """Response to the USSD provider"""

    user: str
    msisdn: str
    message: str
    require_response: bool
