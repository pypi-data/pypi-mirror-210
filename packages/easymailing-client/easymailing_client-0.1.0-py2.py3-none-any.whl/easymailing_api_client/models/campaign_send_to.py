from enum import Enum


class CampaignSendTo(str, Enum):
    SEND_TO_ALL = "send_to_all"
    SEND_TO_GROUPS = "send_to_groups"
    SEND_TO_SEGMENT = "send_to_segment"

    def __str__(self) -> str:
        return str(self.value)
