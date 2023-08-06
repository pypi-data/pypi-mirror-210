from enum import Enum


class SuscriberStatus(str, Enum):
    SUSCRIBER_STATUS_CONFIRMED = "suscriber.status.confirmed"
    SUSCRIBER_STATUS_UNSUSCRIBED = "suscriber.status.unsuscribed"
    SUSCRIBER_STATUS_UNSUSCRIBED_ADMIN = "suscriber.status.unsuscribed.admin"

    def __str__(self) -> str:
        return str(self.value)
