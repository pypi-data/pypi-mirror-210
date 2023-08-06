from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.email_config_jsonld_campaign_create_context_type_1 import EmailConfigJsonldCampaignCreateContextType1


T = TypeVar("T", bound="EmailConfigJsonldCampaignCreate")


@attr.s(auto_attribs=True)
class EmailConfigJsonldCampaignCreate:
    """
    Attributes:
        from_name (str): From name Example: My company.
        from_email (str): Sender email Example: /senders/0df14405-90ff-4287-b3e4-ef088901ee6f.
        reply_to (str): Reply to email Example: /senders/0df14405-90ff-4287-b3e4-ef088901ee6f.
        subject (str): Email subject Example: Check this promotions!.
        context (Union['EmailConfigJsonldCampaignCreateContextType1', Unset, str]):
        id (Union[Unset, str]):
        type (Union[Unset, str]):
        enable_to_name (Union[Unset, bool]): Set the recipient name?
        to_name (Union[Unset, str]): Custom field TAG where you store the suscriber name Example: NAME.
        preview_text (Union[Unset, str]): Preview text Example: 25% discount this month!.
    """

    from_name: str
    from_email: str
    reply_to: str
    subject: str
    context: Union["EmailConfigJsonldCampaignCreateContextType1", Unset, str] = UNSET
    id: Union[Unset, str] = UNSET
    type: Union[Unset, str] = UNSET
    enable_to_name: Union[Unset, bool] = UNSET
    to_name: Union[Unset, str] = UNSET
    preview_text: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.email_config_jsonld_campaign_create_context_type_1 import (
            EmailConfigJsonldCampaignCreateContextType1,
        )

        from_name = self.from_name
        from_email = self.from_email
        reply_to = self.reply_to
        subject = self.subject
        context: Union[Dict[str, Any], Unset, str]
        if isinstance(self.context, Unset):
            context = UNSET

        elif isinstance(self.context, EmailConfigJsonldCampaignCreateContextType1):
            context = UNSET
            if not isinstance(self.context, Unset):
                context = self.context.to_dict()

        else:
            context = self.context

        id = self.id
        type = self.type
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
        if context is not UNSET:
            field_dict["@context"] = context
        if id is not UNSET:
            field_dict["@id"] = id
        if type is not UNSET:
            field_dict["@type"] = type
        if enable_to_name is not UNSET:
            field_dict["enable_to_name"] = enable_to_name
        if to_name is not UNSET:
            field_dict["to_name"] = to_name
        if preview_text is not UNSET:
            field_dict["preview_text"] = preview_text

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.email_config_jsonld_campaign_create_context_type_1 import (
            EmailConfigJsonldCampaignCreateContextType1,
        )

        d = src_dict.copy()
        from_name = d.pop("from_name")

        from_email = d.pop("from_email")

        reply_to = d.pop("reply_to")

        subject = d.pop("subject")

        def _parse_context(data: object) -> Union["EmailConfigJsonldCampaignCreateContextType1", Unset, str]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                _context_type_1 = data
                context_type_1: Union[Unset, EmailConfigJsonldCampaignCreateContextType1]
                if isinstance(_context_type_1, Unset):
                    context_type_1 = UNSET
                else:
                    context_type_1 = EmailConfigJsonldCampaignCreateContextType1.from_dict(_context_type_1)

                return context_type_1
            except:  # noqa: E722
                pass
            return cast(Union["EmailConfigJsonldCampaignCreateContextType1", Unset, str], data)

        context = _parse_context(d.pop("@context", UNSET))

        id = d.pop("@id", UNSET)

        type = d.pop("@type", UNSET)

        enable_to_name = d.pop("enable_to_name", UNSET)

        to_name = d.pop("to_name", UNSET)

        preview_text = d.pop("preview_text", UNSET)

        email_config_jsonld_campaign_create = cls(
            from_name=from_name,
            from_email=from_email,
            reply_to=reply_to,
            subject=subject,
            context=context,
            id=id,
            type=type,
            enable_to_name=enable_to_name,
            to_name=to_name,
            preview_text=preview_text,
        )

        email_config_jsonld_campaign_create.additional_properties = d
        return email_config_jsonld_campaign_create

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
