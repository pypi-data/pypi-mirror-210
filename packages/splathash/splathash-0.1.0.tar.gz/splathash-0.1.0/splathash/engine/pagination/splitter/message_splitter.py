from abc import ABC, abstractmethod
from typing import List


class MessageSplitter(ABC):
    """Split response message into manageable chunks"""

    @abstractmethod
    def should_split(self, message: str) -> bool:
        """check if the message requires splitting"""

    @abstractmethod
    def split(self, message: str) -> List[str]:
        """split message into chunks"""


class DefaultMessageSplitter(MessageSplitter):
    """Split messages into a defined chunk size"""

    message_limit: int = 130

    def should_split(self, message: str) -> bool:
        return len(message) > self.message_limit

    def split(self, message: str) -> List[str]:
        separator = "\n"
        tokens = message.split(separator)
        pages = self.join(tokens, separator)

        output = []
        for page in pages:
            if self.should_split(page):
                separator = " "
                sub_tokens = page.split(separator)
                sub_pages = self.join(sub_tokens, separator)
                for sub in sub_pages:
                    output.append(sub)
            else:
                output.append(page)

        return pages

    def join(self, tokens: List[str], separator: str) -> List[str]:
        pages = []
        page = ""

        for token in tokens:
            new_page = f"{page}{separator}{token}".strip()
            if len(new_page) <= self.message_limit:
                page = new_page
            else:
                pages.append(page)
                page = token

        pages.append(page)

        pages = list(filter(lambda m: len(m.strip()) > 0, pages))
        return pages


class MessageSplitterFactory:
    @staticmethod
    def default() -> MessageSplitter:
        return DefaultMessageSplitter()
