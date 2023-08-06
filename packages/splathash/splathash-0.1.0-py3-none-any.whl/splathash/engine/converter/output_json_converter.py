from abc import ABC, abstractmethod

from splathash.data.output_data import OutputData


class OutputJsonConverter(ABC):
    """Convert output data to string"""

    @abstractmethod
    def to_json(self, output_data: OutputData) -> dict:
        """Convert to dict"""


class NALOOutputJsonConverter(OutputJsonConverter):
    """Convert output data to dict with NALO keys"""

    def to_json(self, output_data: OutputData) -> dict:
        return {
            "USERID": output_data.user,
            "MSISDN": output_data.msisdn,
            "MSG": output_data.message,
            "MSGTYPE": output_data.require_response,
        }


class OutputJsonConverterFactory:
    @staticmethod
    def default() -> OutputJsonConverter:
        return NALOOutputJsonConverter()
