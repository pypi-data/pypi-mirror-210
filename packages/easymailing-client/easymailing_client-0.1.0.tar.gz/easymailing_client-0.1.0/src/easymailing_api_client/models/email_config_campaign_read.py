from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="EmailConfigCampaignRead")


@attr.s(auto_attribs=True)
class EmailConfigCampaignRead:
    """
    Attributes:
        from_name (Union[Unset, None, str]):
        enable_to_name (Union[Unset, None, bool]):
        to_name (Union[Unset, None, str]):
        subject (Union[Unset, None, str]):
        preview_text (Union[Unset, None, str]):
        from_email (Union[Unset, None, str]):
        reply_to (Union[Unset, None, str]):
    """

    from_name: Union[Unset, None, str] = UNSET
    enable_to_name: Union[Unset, None, bool] = UNSET
    to_name: Union[Unset, None, str] = UNSET
    subject: Union[Unset, None, str] = UNSET
    preview_text: Union[Unset, None, str] = UNSET
    from_email: Union[Unset, None, str] = UNSET
    reply_to: Union[Unset, None, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from_name = self.from_name
        enable_to_name = self.enable_to_name
        to_name = self.to_name
        subject = self.subject
        preview_text = self.preview_text
        from_email = self.from_email
        reply_to = self.reply_to

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if from_name is not UNSET:
            field_dict["from_name"] = from_name
        if enable_to_name is not UNSET:
            field_dict["enable_to_name"] = enable_to_name
        if to_name is not UNSET:
            field_dict["to_name"] = to_name
        if subject is not UNSET:
            field_dict["subject"] = subject
        if preview_text is not UNSET:
            field_dict["preview_text"] = preview_text
        if from_email is not UNSET:
            field_dict["from_email"] = from_email
        if reply_to is not UNSET:
            field_dict["reply_to"] = reply_to

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        from_name = d.pop("from_name", UNSET)

        enable_to_name = d.pop("enable_to_name", UNSET)

        to_name = d.pop("to_name", UNSET)

        subject = d.pop("subject", UNSET)

        preview_text = d.pop("preview_text", UNSET)

        from_email = d.pop("from_email", UNSET)

        reply_to = d.pop("reply_to", UNSET)

        email_config_campaign_read = cls(
            from_name=from_name,
            enable_to_name=enable_to_name,
            to_name=to_name,
            subject=subject,
            preview_text=preview_text,
            from_email=from_email,
            reply_to=reply_to,
        )

        email_config_campaign_read.additional_properties = d
        return email_config_campaign_read

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
