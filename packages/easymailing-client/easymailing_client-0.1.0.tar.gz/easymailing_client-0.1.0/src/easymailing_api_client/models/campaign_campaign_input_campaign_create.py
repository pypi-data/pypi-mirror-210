from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..models.campaign_send_to import CampaignSendTo
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.campaign_config_campaign_create import CampaignConfigCampaignCreate
    from ..models.email_config_campaign_create import EmailConfigCampaignCreate


T = TypeVar("T", bound="CampaignCampaignInputCampaignCreate")


@attr.s(auto_attribs=True)
class CampaignCampaignInputCampaignCreate:
    """
    Attributes:
        title (str): Campaign title Example: My Awesome Campaign!.
        email_config (EmailConfigCampaignCreate):
        campaign_config (CampaignConfigCampaignCreate):
        audience (str): Audience Example: /audiences/0df14405-90ff-4287-b3e4-ef088901ee6f.
        send_to (CampaignSendTo): Campaign sendTo:
            * `send_to_all` - Send to all
            * `send_to_segment` - Send to a saved segment
            * `send_to_groups` - Send to one or more groups
        template (Union[Unset, str]): Template Example: /templates/0df14405-90ff-4287-b3e4-ef088901ee6f.
        template_html (Union[Unset, str]): Email html if you dont send a Template Example: <html><body><p>My awesome
            template!</p></body</html>.
        list_segment (Union[Unset, str]): List Segment Example: /list_segments/0df14405-90ff-4287-b3e4-ef088901ee6f.
        groups (Union[Unset, List[str]]): Groups
    """

    title: str
    email_config: "EmailConfigCampaignCreate"
    campaign_config: "CampaignConfigCampaignCreate"
    audience: str
    send_to: CampaignSendTo
    template: Union[Unset, str] = UNSET
    template_html: Union[Unset, str] = UNSET
    list_segment: Union[Unset, str] = UNSET
    groups: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        title = self.title
        email_config = self.email_config.to_dict()

        campaign_config = self.campaign_config.to_dict()

        audience = self.audience
        send_to = self.send_to.value

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
        from ..models.campaign_config_campaign_create import CampaignConfigCampaignCreate
        from ..models.email_config_campaign_create import EmailConfigCampaignCreate

        d = src_dict.copy()
        title = d.pop("title")

        email_config = EmailConfigCampaignCreate.from_dict(d.pop("email_config"))

        campaign_config = CampaignConfigCampaignCreate.from_dict(d.pop("campaign_config"))

        audience = d.pop("audience")

        send_to = CampaignSendTo(d.pop("send_to"))

        template = d.pop("template", UNSET)

        template_html = d.pop("template_html", UNSET)

        list_segment = d.pop("list_segment", UNSET)

        groups = cast(List[str], d.pop("groups", UNSET))

        campaign_campaign_input_campaign_create = cls(
            title=title,
            email_config=email_config,
            campaign_config=campaign_config,
            audience=audience,
            send_to=send_to,
            template=template,
            template_html=template_html,
            list_segment=list_segment,
            groups=groups,
        )

        campaign_campaign_input_campaign_create.additional_properties = d
        return campaign_campaign_input_campaign_create

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
