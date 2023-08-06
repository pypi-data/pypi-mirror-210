from abc import ABC, abstractmethod
from typing import List

from splathash.engine.context.application_context import ApplicationContext


class PaginationContext(ABC):
    """Context for pagination"""

    @abstractmethod
    def initialize(self, context: ApplicationContext, data: dict) -> None:
        """Begin or resume the pagination session"""

    @abstractmethod
    def flag(self, flag: bool = None) -> bool:
        """Set and retrieve paging flag"""

    @abstractmethod
    def pages(self, pages: List[str] = None) -> List[str]:
        """Set and retrieve pages"""

    @abstractmethod
    def current_page(self, number: int = None) -> int:
        """Set and retrieve current page"""

    @abstractmethod
    def response(self, data: dict = None) -> dict:
        """Set and retrieve response"""


class NALOPaginationContext(PaginationContext):
    """Cater to NALO specific data format, using django db session"""

    context: ApplicationContext
    __PAGING = "__PAGING"
    __PAGES = "__PAGES"
    __CURRENT = "__CURRENT"
    __RESPONSE = "__RESPONSE"

    def initialize(self, context: ApplicationContext, data: dict) -> None:
        """Initialize the context with a modified msisdn"""
        self.context = context
        self.context.initialize(data={**data, "MSISDN": f"P{data['MSISDN']}"})

    def flag(self, flag: bool = None) -> bool:
        if flag is None:
            return self.context.retrieve(key=self.__PAGING) or False

        self.context.update(key=self.__PAGING, value=flag)
        return flag

    def pages(self, pages: List[str] = None) -> List[str]:
        if pages is None:
            return self.context.retrieve(key=self.__PAGES) or []

        self.context.update(key=self.__PAGES, value=pages)
        return pages

    def current_page(self, number: int = None) -> int:
        if number is None:
            return self.context.retrieve(key=self.__CURRENT) or 0

        self.context.update(key=self.__CURRENT, value=number)
        return number

    def response(self, data: dict = None) -> dict:
        if data is None:
            return self.context.retrieve(key=self.__RESPONSE) or {}

        self.context.update(key=self.__RESPONSE, value=data)
        return data


class PaginationContextFactory:
    @staticmethod
    def default() -> PaginationContext:
        return NALOPaginationContext()
