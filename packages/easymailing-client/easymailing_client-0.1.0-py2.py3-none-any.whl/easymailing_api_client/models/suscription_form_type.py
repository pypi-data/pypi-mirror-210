from enum import Enum


class SuscriptionFormType(str, Enum):
    EMBEDDED = "embedded"
    POPUP = "popup"

    def __str__(self) -> str:
        return str(self.value)
