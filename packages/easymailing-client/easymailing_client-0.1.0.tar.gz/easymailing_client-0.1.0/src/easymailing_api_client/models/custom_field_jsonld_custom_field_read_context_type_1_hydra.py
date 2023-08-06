from enum import Enum


class CustomFieldJsonldCustomFieldReadContextType1Hydra(str, Enum):
    HTTPWWW_W3_ORGNSHYDRACORE = "http://www.w3.org/ns/hydra/core#"

    def __str__(self) -> str:
        return str(self.value)
