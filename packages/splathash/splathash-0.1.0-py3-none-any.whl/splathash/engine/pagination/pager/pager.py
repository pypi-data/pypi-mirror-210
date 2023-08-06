from abc import ABC, abstractmethod
from typing import List


class Pager(ABC):
    """Create pages"""

    @abstractmethod
    def create_pages(self, messages: List[str], next_key: str, previous_key: str) -> List[str]:
        """modify list of string with navigation options"""


class DefaultPager(Pager):
    """add next and previous key and text"""

    def create_pages(self, messages: List[str], next_key: str, previous_key: str) -> List[str]:
        last_index = len(messages) - 1
        next_text = f"{next_key} Next"
        previous_text = f"{previous_key} Previous"
        empty = ""
        new_line = "\n"
        return [
            f"{message}"
            f"{(new_line + next_text) if index < last_index else empty}"
            f"{(new_line + previous_text) if index > 0 else empty}"
            for index, message in enumerate(messages)
        ]


class PagerFactory:
    @staticmethod
    def default():
        return DefaultPager()
