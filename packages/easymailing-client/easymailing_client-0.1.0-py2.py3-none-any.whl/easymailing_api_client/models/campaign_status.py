from enum import Enum


class CampaignStatus(str, Enum):
    CAMPAIGN_STATUS_DRAFT = "campaign.status.draft"
    CAMPAIGN_STATUS_ERROR = "campaign.status.error"
    CAMPAIGN_STATUS_PAUSED = "campaign.status.paused"
    CAMPAIGN_STATUS_PAUSING = "campaign.status.pausing"
    CAMPAIGN_STATUS_READY = "campaign.status.ready"
    CAMPAIGN_STATUS_SCHEDULED = "campaign.status.scheduled"
    CAMPAIGN_STATUS_SENDING = "campaign.status.sending"
    CAMPAIGN_STATUS_SENT = "campaign.status.sent"

    def __str__(self) -> str:
        return str(self.value)
