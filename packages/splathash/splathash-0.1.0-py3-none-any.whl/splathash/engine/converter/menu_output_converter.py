from abc import ABC, abstractmethod

from splathash.data.node_response import NodeResponse
from splathash.data.output_data import OutputData
from splathash.engine.context.application_context import ApplicationContext


class MenuOutputConverter(ABC):
    """Converts a node response to an output data"""

    @abstractmethod
    def convert(self, node_response: NodeResponse, context: ApplicationContext) -> OutputData:
        """Convert node response with data from the application context"""


class DefaultOutputConverter(MenuOutputConverter):
    """Default converter"""

    def convert(self, node_response: NodeResponse, context: ApplicationContext) -> OutputData:
        text = node_response.message
        for option in node_response.options:
            text = f"{text}\n{option.number}. {option.text}"

        input_data = context.input_data()

        continue_ussd = len(node_response.options) > 0 or node_response.require_response

        return OutputData(
            user=input_data.user,
            msisdn=input_data.msisdn,
            message=text.strip(),
            require_response=continue_ussd,
        )


class MenuOutputConverterFactory:
    @staticmethod
    def default() -> MenuOutputConverter:
        return DefaultOutputConverter()
