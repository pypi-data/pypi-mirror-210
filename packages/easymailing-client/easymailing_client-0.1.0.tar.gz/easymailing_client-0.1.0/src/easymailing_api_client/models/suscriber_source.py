from enum import Enum


class SuscriberSource(str, Enum):
    SUSCRIBER_SOURCE_API = "suscriber.source.api"
    SUSCRIBER_SOURCE_IMPORTED = "suscriber.source.imported"
    SUSCRIBER_SOURCE_MANUAL = "suscriber.source.manual"
    SUSCRIBER_SOURCE_WEBFORM = "suscriber.source.webform"

    def __str__(self) -> str:
        return str(self.value)
