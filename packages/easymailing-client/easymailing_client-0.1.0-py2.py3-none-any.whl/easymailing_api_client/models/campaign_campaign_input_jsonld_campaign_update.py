from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..models.campaign_send_to import CampaignSendTo
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.campaign_campaign_input_jsonld_campaign_update_context_type_1 import (
        CampaignCampaignInputJsonldCampaignUpdateContextType1,
    )
    from ..models.campaign_config_jsonld_campaign_update import CampaignConfigJsonldCampaignUpdate
    from ..models.email_config_jsonld_campaign_update import EmailConfigJsonldCampaignUpdate


T = TypeVar("T", bound="CampaignCampaignInputJsonldCampaignUpdate")


@attr.s(auto_attribs=True)
class CampaignCampaignInputJsonldCampaignUpdate:
    """
    Attributes:
        title (str): Campaign title Example: My Awesome Campaign!.
        email_config (EmailConfigJsonldCampaignUpdate):
        campaign_config (CampaignConfigJsonldCampaignUpdate):
        audience (str): Audience Example: /audiences/0df14405-90ff-4287-b3e4-ef088901ee6f.
        send_to (CampaignSendTo): Campaign sendTo:
            * `send_to_all` - Send to all
            * `send_to_segment` - Send to a saved segment
            * `send_to_groups` - Send to one or more groups
        context (Union['CampaignCampaignInputJsonldCampaignUpdateContextType1', Unset, str]):
        id (Union[Unset, str]):
        type (Union[Unset, str]):
        template (Union[Unset, str]): Template Example: /templates/0df14405-90ff-4287-b3e4-ef088901ee6f.
        template_html (Union[Unset, str]): Email html if you dont send a Template Example: <html><body><p>My awesome
            template!</p></body</html>.
        list_segment (Union[Unset, str]): List Segment Example: /list_segments/0df14405-90ff-4287-b3e4-ef088901ee6f.
        groups (Union[Unset, List[str]]): Groups
    """

    title: str
    email_config: "EmailConfigJsonldCampaignUpdate"
    campaign_config: "CampaignConfigJsonldCampaignUpdate"
    audience: str
    send_to: CampaignSendTo
    context: Union["CampaignCampaignInputJsonldCampaignUpdateContextType1", Unset, str] = UNSET
    id: Union[Unset, str] = UNSET
    type: Union[Unset, str] = UNSET
    template: Union[Unset, str] = UNSET
    template_html: Union[Unset, str] = UNSET
    list_segment: Union[Unset, str] = UNSET
    groups: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.campaign_campaign_input_jsonld_campaign_update_context_type_1 import (
            CampaignCampaignInputJsonldCampaignUpdateContextType1,
        )

        title = self.title
        email_config = self.email_config.to_dict()

        campaign_config = self.campaign_config.to_dict()

        audience = self.audience
        send_to = self.send_to.value

        context: Union[Dict[str, Any], Unset, str]
        if isinstance(self.context, Unset):
            context = UNSET

        elif isinstance(self.context, CampaignCampaignInputJsonldCampaignUpdateContextType1):
            context = UNSET
            if not isinstance(self.context, Unset):
                context = self.context.to_dict()

        else:
            context = self.context

        id = self.id
        type = self.type
        template = self.template
        template_html = self.template_html
        list_segment = self.list_segment
        groups: Union[Unset, List[str]] = UNSET
        if not isinstance(self.groups, Unset):
            groups = self.groups

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "title": title,
                "email_config": email_config,
                "campaign_config": campaign_config,
                "audience": audience,
                "send_to": send_to,
            }
        )
        if context is not UNSET:
            field_dict["@context"] = context
        if id is not UNSET:
            field_dict["@id"] = id
        if type is not UNSET:
            field_dict["@type"] = type
        if template is not UNSET:
            field_dict["template"] = template
        if template_html is not UNSET:
            field_dict["template_html"] = template_html
        if list_segment is not UNSET:
            field_dict["list_segment"] = list_segment
        if groups is not UNSET:
            field_dict["groups"] = groups

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.campaign_campaign_input_jsonld_campaign_update_context_type_1 import (
            CampaignCampaignInputJsonldCampaignUpdateContextType1,
        )
        from ..models.campaign_config_jsonld_campaign_update import CampaignConfigJsonldCampaignUpdate
        from ..models.email_config_jsonld_campaign_update import EmailConfigJsonldCampaignUpdate

        d = src_dict.copy()
        title = d.pop("title")

        email_config = EmailConfigJsonldCampaignUpdate.from_dict(d.pop("email_config"))

        campaign_config = CampaignConfigJsonldCampaignUpdate.from_dict(d.pop("campaign_config"))

        audience = d.pop("audience")

        send_to = CampaignSendTo(d.pop("send_to"))

        def _parse_context(data: object) -> Union["CampaignCampaignInputJsonldCampaignUpdateContextType1", Unset, str]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                _context_type_1 = data
                context_type_1: Union[Unset, CampaignCampaignInputJsonldCampaignUpdateContextType1]
                if isinstance(_context_type_1, Unset):
                    context_type_1 = UNSET
                else:
                    context_type_1 = CampaignCampaignInputJsonldCampaignUpdateContextType1.from_dict(_context_type_1)

                return context_type_1
            except:  # noqa: E722
                pass
            return cast(Union["CampaignCampaignInputJsonldCampaignUpdateContextType1", Unset, str], data)

        context = _parse_context(d.pop("@context", UNSET))

        id = d.pop("@id", UNSET)

        type = d.pop("@type", UNSET)

        template = d.pop("template", UNSET)

        template_html = d.pop("template_html", UNSET)

        list_segment = d.pop("list_segment", UNSET)

        groups = cast(List[str], d.pop("groups", UNSET))

        campaign_campaign_input_jsonld_campaign_update = cls(
            title=title,
            email_config=email_config,
            campaign_config=campaign_config,
            audience=audience,
            send_to=send_to,
            context=context,
            id=id,
            type=type,
            template=template,
            template_html=template_html,
            list_segment=list_segment,
            groups=groups,
        )

        campaign_campaign_input_jsonld_campaign_update.additional_properties = d
        return campaign_campaign_input_jsonld_campaign_update

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
