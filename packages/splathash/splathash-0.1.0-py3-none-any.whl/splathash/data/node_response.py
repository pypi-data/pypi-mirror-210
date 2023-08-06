from dataclasses import dataclass, field
from typing import List


@dataclass
class MenuOption:
    """Options for user to select from"""

    number: str
    text: str


@dataclass
class NodeResponse:
    """Response from node processing data"""

    message: str
    options: List[MenuOption] = field(default_factory=lambda: [])
    require_response: bool = False

    def add_option(self, number: str, text: str) -> None:
        if self.options is None:
            self.options = []

        self.options.append(MenuOption(number, text))

    def add_multiple_options(self, options: dict) -> None:
        if self.options is None:
            self.options = []

        for key in options.keys():
            self.options.append(MenuOption(key, options[key]))
