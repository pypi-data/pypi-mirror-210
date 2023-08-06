from abc import ABC, abstractmethod
from typing import Tuple

from splathash.data.node_response import NodeResponse
from splathash.engine.context.application_context import ApplicationContext


class Node(ABC):
    """A node describes a single screen"""

    @abstractmethod
    def create_menu(self, context: ApplicationContext) -> Tuple[NodeResponse, str]:
        """Prepare response to user input"""
