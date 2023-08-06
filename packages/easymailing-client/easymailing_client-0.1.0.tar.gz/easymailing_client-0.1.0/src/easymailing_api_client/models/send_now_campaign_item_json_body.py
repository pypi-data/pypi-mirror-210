from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="SendNowCampaignItemJsonBody")


@attr.s(auto_attribs=True)
class SendNowCampaignItemJsonBody:
    """
    Attributes:
        send_confirmation_email (Union[Unset, bool]): Send a confirmation email when the campaign get sent Example:
            True.
        mailing_confirm_emails (Union[Unset, List[str]]): Emails to send the confirmation Example: ['user1@company.com',
            'user2@company.com'].
    """

    send_confirmation_email: Union[Unset, bool] = UNSET
    mailing_confirm_emails: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        send_confirmation_email = self.send_confirmation_email
        mailing_confirm_emails: Union[Unset, List[str]] = UNSET
        if not isinstance(self.mailing_confirm_emails, Unset):
            mailing_confirm_emails = []
            for mailing_confirm_emails_item_data in self.mailing_confirm_emails:
                mailing_confirm_emails_item: str

                mailing_confirm_emails_item = mailing_confirm_emails_item_data

                mailing_confirm_emails.append(mailing_confirm_emails_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if send_confirmation_email is not UNSET:
            field_dict["send_confirmation_email"] = send_confirmation_email
        if mailing_confirm_emails is not UNSET:
            field_dict["mailing_confirm_emails"] = mailing_confirm_emails

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        send_confirmation_email = d.pop("send_confirmation_email", UNSET)

        mailing_confirm_emails = []
        _mailing_confirm_emails = d.pop("mailing_confirm_emails", UNSET)
        for mailing_confirm_emails_item_data in _mailing_confirm_emails or []:

            def _parse_mailing_confirm_emails_item(data: object) -> str:
                return cast(str, data)

            mailing_confirm_emails_item = _parse_mailing_confirm_emails_item(mailing_confirm_emails_item_data)

            mailing_confirm_emails.append(mailing_confirm_emails_item)

        send_now_campaign_item_json_body = cls(
            send_confirmation_email=send_confirmation_email,
            mailing_confirm_emails=mailing_confirm_emails,
        )

        send_now_campaign_item_json_body.additional_properties = d
        return send_now_campaign_item_json_body

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
