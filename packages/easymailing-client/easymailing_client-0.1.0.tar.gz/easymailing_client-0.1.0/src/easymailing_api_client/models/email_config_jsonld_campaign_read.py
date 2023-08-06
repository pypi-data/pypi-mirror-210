from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.email_config_jsonld_campaign_read_context_type_1 import EmailConfigJsonldCampaignReadContextType1


T = TypeVar("T", bound="EmailConfigJsonldCampaignRead")


@attr.s(auto_attribs=True)
class EmailConfigJsonldCampaignRead:
    """
    Attributes:
        id (Union[Unset, str]):
        type (Union[Unset, str]):
        context (Union['EmailConfigJsonldCampaignReadContextType1', Unset, str]):
        from_name (Union[Unset, None, str]):
        enable_to_name (Union[Unset, None, bool]):
        to_name (Union[Unset, None, str]):
        subject (Union[Unset, None, str]):
        preview_text (Union[Unset, None, str]):
        from_email (Union[Unset, None, str]):
        reply_to (Union[Unset, None, str]):
    """

    id: Union[Unset, str] = UNSET
    type: Union[Unset, str] = UNSET
    context: Union["EmailConfigJsonldCampaignReadContextType1", Unset, str] = UNSET
    from_name: Union[Unset, None, str] = UNSET
    enable_to_name: Union[Unset, None, bool] = UNSET
    to_name: Union[Unset, None, str] = UNSET
    subject: Union[Unset, None, str] = UNSET
    preview_text: Union[Unset, None, str] = UNSET
    from_email: Union[Unset, None, str] = UNSET
    reply_to: Union[Unset, None, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.email_config_jsonld_campaign_read_context_type_1 import EmailConfigJsonldCampaignReadContextType1

        id = self.id
        type = self.type
        context: Union[Dict[str, Any], Unset, str]
        if isinstance(self.context, Unset):
            context = UNSET

        elif isinstance(self.context, EmailConfigJsonldCampaignReadContextType1):
            context = UNSET
            if not isinstance(self.context, Unset):
                context = self.context.to_dict()

        else:
            context = self.context

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
        if id is not UNSET:
            field_dict["@id"] = id
        if type is not UNSET:
            field_dict["@type"] = type
        if context is not UNSET:
            field_dict["@context"] = context
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
        from ..models.email_config_jsonld_campaign_read_context_type_1 import EmailConfigJsonldCampaignReadContextType1

        d = src_dict.copy()
        id = d.pop("@id", UNSET)

        type = d.pop("@type", UNSET)

        def _parse_context(data: object) -> Union["EmailConfigJsonldCampaignReadContextType1", Unset, str]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                _context_type_1 = data
                context_type_1: Union[Unset, EmailConfigJsonldCampaignReadContextType1]
                if isinstance(_context_type_1, Unset):
                    context_type_1 = UNSET
                else:
                    context_type_1 = EmailConfigJsonldCampaignReadContextType1.from_dict(_context_type_1)

                return context_type_1
            except:  # noqa: E722
                pass
            return cast(Union["EmailConfigJsonldCampaignReadContextType1", Unset, str], data)

        context = _parse_context(d.pop("@context", UNSET))

        from_name = d.pop("from_name", UNSET)

        enable_to_name = d.pop("enable_to_name", UNSET)

        to_name = d.pop("to_name", UNSET)

        subject = d.pop("subject", UNSET)

        preview_text = d.pop("preview_text", UNSET)

        from_email = d.pop("from_email", UNSET)

        reply_to = d.pop("reply_to", UNSET)

        email_config_jsonld_campaign_read = cls(
            id=id,
            type=type,
            context=context,
            from_name=from_name,
            enable_to_name=enable_to_name,
            to_name=to_name,
            subject=subject,
            preview_text=preview_text,
            from_email=from_email,
            reply_to=reply_to,
        )

        email_config_jsonld_campaign_read.additional_properties = d
        return email_config_jsonld_campaign_read

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
