from abc import ABC, abstractmethod

from splathash.engine.context.application_context import ApplicationContext
from splathash.node.node import Node


class UserResponseHandler(ABC):
    """
    Finds the correct node to move to based on the response to the last question
    and application context
    """

    @abstractmethod
    def get_node(self, context: ApplicationContext) -> Node:
        """
        Use context.data to get latest input data and context.retrieve(key, default)
        to fetch a specific data
        """
