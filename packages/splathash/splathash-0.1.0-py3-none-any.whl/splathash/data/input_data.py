from dataclasses import dataclass


@dataclass
class InputData:
    """Incoming data from the USSD provider"""

    msisdn: str
    network: str
    data: str
    start: bool
    user: str
