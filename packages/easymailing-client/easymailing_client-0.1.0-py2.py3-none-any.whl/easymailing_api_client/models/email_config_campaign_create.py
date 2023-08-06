from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="EmailConfigCampaignCreate")


@attr.s(auto_attribs=True)
class EmailConfigCampaignCreate:
    """
    Attributes:
        from_name (str): From name Example: My company.
        from_email (str): Sender email Example: /senders/0df14405-90ff-4287-b3e4-ef088901ee6f.
        reply_to (str): Reply to email Example: /senders/0df14405-90ff-4287-b3e4-ef088901ee6f.
        subject (str): Email subject Example: Check this promotions!.
        enable_to_name (Union[Unset, bool]): Set the recipient name?
        to_name (Union[Unset, str]): Custom field TAG where you store the suscriber name Example: NAME.
        preview_text (Union[Unset, str]): Preview text Example: 25% discount this month!.
    """

    from_name: str
    from_email: str
    reply_to: str
    subject: str
    enable_to_name: Union[Unset, bool] = UNSET
    to_name: Union[Unset, str] = UNSET
    preview_text: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from_name = self.from_name
        from_email = self.from_email
        reply_to = self.reply_to
        subject = self.subject
        enable_to_name = self.enable_to_name
        to_name = self.to_name
        preview_text = self.preview_text

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "from_name": from_name,
                "from_email": from_email,
                "reply_to": reply_to,
                "subject": subject,
            }
        )
        if enable_to_name is not UNSET:
            field_dict["enable_to_name"] = enable_to_name
        if to_name is not UNSET:
            field_dict["to_name"] = to_name
        if preview_text is not UNSET:
            field_dict["preview_text"] = preview_text

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        from_name = d.pop("from_name")

        from_email = d.pop("from_email")

        reply_to = d.pop("reply_to")

        subject = d.pop("subject")

        enable_to_name = d.pop("enable_to_name", UNSET)

        to_name = d.pop("to_name", UNSET)

        preview_text = d.pop("preview_text", UNSET)

        email_config_campaign_create = cls(
            from_name=from_name,
            from_email=from_email,
            reply_to=reply_to,
            subject=subject,
            enable_to_name=enable_to_name,
            to_name=to_name,
            preview_text=preview_text,
        )

        email_config_campaign_create.additional_properties = d
        return email_config_campaign_create

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
