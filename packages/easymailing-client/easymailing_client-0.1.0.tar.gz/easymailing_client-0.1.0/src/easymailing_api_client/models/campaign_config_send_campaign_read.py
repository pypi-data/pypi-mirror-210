import datetime
from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="CampaignConfigSendCampaignRead")


@attr.s(auto_attribs=True)
class CampaignConfigSendCampaignRead:
    """
    Attributes:
        schedule_mailling (Union[Unset, None, bool]): Schedule the campaign
        schedule_mailling_date (Union[Unset, None, datetime.datetime]): Schedule date to send the campaign
        send_confirmation_email (Union[Unset, None, bool]): Send a confirmation email when the campaign get sent
            Example: True.
        mailing_confirm_emails (Union[Unset, None, List[str]]): Emails to send the confirmation Example:
            ['user1@company.com', 'user2@company.com'].
    """

    schedule_mailling: Union[Unset, None, bool] = UNSET
    schedule_mailling_date: Union[Unset, None, datetime.datetime] = UNSET
    send_confirmation_email: Union[Unset, None, bool] = UNSET
    mailing_confirm_emails: Union[Unset, None, List[str]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        schedule_mailling = self.schedule_mailling
        schedule_mailling_date: Union[Unset, None, str] = UNSET
        if not isinstance(self.schedule_mailling_date, Unset):
            schedule_mailling_date = self.schedule_mailling_date.isoformat() if self.schedule_mailling_date else None

        send_confirmation_email = self.send_confirmation_email
        mailing_confirm_emails: Union[Unset, None, List[str]] = UNSET
        if not isinstance(self.mailing_confirm_emails, Unset):
            if self.mailing_confirm_emails is None:
                mailing_confirm_emails = None
            else:
                mailing_confirm_emails = []
                for mailing_confirm_emails_item_data in self.mailing_confirm_emails:
                    mailing_confirm_emails_item: str

                    mailing_confirm_emails_item = mailing_confirm_emails_item_data

                    mailing_confirm_emails.append(mailing_confirm_emails_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if schedule_mailling is not UNSET:
            field_dict["schedule_mailling"] = schedule_mailling
        if schedule_mailling_date is not UNSET:
            field_dict["schedule_mailling_date"] = schedule_mailling_date
        if send_confirmation_email is not UNSET:
            field_dict["send_confirmation_email"] = send_confirmation_email
        if mailing_confirm_emails is not UNSET:
            field_dict["mailing_confirm_emails"] = mailing_confirm_emails

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        schedule_mailling = d.pop("schedule_mailling", UNSET)

        _schedule_mailling_date = d.pop("schedule_mailling_date", UNSET)
        schedule_mailling_date: Union[Unset, None, datetime.datetime]
        if _schedule_mailling_date is None:
            schedule_mailling_date = None
        elif isinstance(_schedule_mailling_date, Unset):
            schedule_mailling_date = UNSET
        else:
            schedule_mailling_date = isoparse(_schedule_mailling_date)

        send_confirmation_email = d.pop("send_confirmation_email", UNSET)

        mailing_confirm_emails = []
        _mailing_confirm_emails = d.pop("mailing_confirm_emails", UNSET)
        for mailing_confirm_emails_item_data in _mailing_confirm_emails or []:

            def _parse_mailing_confirm_emails_item(data: object) -> str:
                return cast(str, data)

            mailing_confirm_emails_item = _parse_mailing_confirm_emails_item(mailing_confirm_emails_item_data)

            mailing_confirm_emails.append(mailing_confirm_emails_item)

        campaign_config_send_campaign_read = cls(
            schedule_mailling=schedule_mailling,
            schedule_mailling_date=schedule_mailling_date,
            send_confirmation_email=send_confirmation_email,
            mailing_confirm_emails=mailing_confirm_emails,
        )

        campaign_config_send_campaign_read.additional_properties = d
        return campaign_config_send_campaign_read

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
