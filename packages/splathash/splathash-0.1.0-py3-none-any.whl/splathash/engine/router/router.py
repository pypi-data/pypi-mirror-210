from abc import ABC, abstractmethod

from splathash.response.response_handler import UserResponseHandler


class Router(ABC):
    """Find the appropriate node to handle user input based on the next route string"""

    @abstractmethod
    def route(self, route: str) -> UserResponseHandler:
        """Fetch correct router"""


class BaseLookupTableRouter(Router, ABC):
    """Use a routing table to route"""

    table: dict = {}
    """ Override the table to use the router """

    def route(self, route: str) -> UserResponseHandler:
        """lookup the route and return an appropriate response handler"""
        handler = self.table.get(route)
        if handler is None:
            raise Exception(f"No handler for the given route: {route}")

        return handler()
