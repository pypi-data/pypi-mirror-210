import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

import attr
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.campaign_config_jsonld_campaign_read import CampaignConfigJsonldCampaignRead
    from ..models.campaign_config_send_jsonld_campaign_read import CampaignConfigSendJsonldCampaignRead
    from ..models.campaign_jsonld_campaign_read_context_type_1 import CampaignJsonldCampaignReadContextType1
    from ..models.campaign_send_stat_jsonld_campaign_read import CampaignSendStatJsonldCampaignRead
    from ..models.email_config_jsonld_campaign_read import EmailConfigJsonldCampaignRead
    from ..models.list_segment_jsonld_campaign_read import ListSegmentJsonldCampaignRead


T = TypeVar("T", bound="CampaignJsonldCampaignRead")


@attr.s(auto_attribs=True)
class CampaignJsonldCampaignRead:
    """
    Attributes:
        context (Union['CampaignJsonldCampaignReadContextType1', Unset, str]):
        id (Union[Unset, str]):
        type (Union[Unset, str]):
        title (Union[Unset, None, str]):
        status (Union[Unset, None, str]):
        template_html (Union[Unset, None, str]):
        template_thumbnail (Union[Unset, None, str]):
        email_config (Union[Unset, None, EmailConfigJsonldCampaignRead]):
        campaign_config (Union[Unset, None, CampaignConfigJsonldCampaignRead]):
        campaign_config_send (Union[Unset, None, CampaignConfigSendJsonldCampaignRead]):
        campaign_send_stat (Union[Unset, None, CampaignSendStatJsonldCampaignRead]):
        template (Union[Unset, None, str]):
        audience (Union[Unset, None, str]):
        list_segment (Union[Unset, None, ListSegmentJsonldCampaignRead]):
        send_to (Union[Unset, None, str]):
        created_at (Union[Unset, None, datetime.datetime]):
        updated_at (Union[Unset, None, datetime.datetime]):
    """

    context: Union["CampaignJsonldCampaignReadContextType1", Unset, str] = UNSET
    id: Union[Unset, str] = UNSET
    type: Union[Unset, str] = UNSET
    title: Union[Unset, None, str] = UNSET
    status: Union[Unset, None, str] = UNSET
    template_html: Union[Unset, None, str] = UNSET
    template_thumbnail: Union[Unset, None, str] = UNSET
    email_config: Union[Unset, None, "EmailConfigJsonldCampaignRead"] = UNSET
    campaign_config: Union[Unset, None, "CampaignConfigJsonldCampaignRead"] = UNSET
    campaign_config_send: Union[Unset, None, "CampaignConfigSendJsonldCampaignRead"] = UNSET
    campaign_send_stat: Union[Unset, None, "CampaignSendStatJsonldCampaignRead"] = UNSET
    template: Union[Unset, None, str] = UNSET
    audience: Union[Unset, None, str] = UNSET
    list_segment: Union[Unset, None, "ListSegmentJsonldCampaignRead"] = UNSET
    send_to: Union[Unset, None, str] = UNSET
    created_at: Union[Unset, None, datetime.datetime] = UNSET
    updated_at: Union[Unset, None, datetime.datetime] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.campaign_jsonld_campaign_read_context_type_1 import CampaignJsonldCampaignReadContextType1

        context: Union[Dict[str, Any], Unset, str]
        if isinstance(self.context, Unset):
            context = UNSET

        elif isinstance(self.context, CampaignJsonldCampaignReadContextType1):
            context = UNSET
            if not isinstance(self.context, Unset):
                context = self.context.to_dict()

        else:
            context = self.context

        id = self.id
        type = self.type
        title = self.title
        status = self.status
        template_html = self.template_html
        template_thumbnail = self.template_thumbnail
        email_config: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.email_config, Unset):
            email_config = self.email_config.to_dict() if self.email_config else None

        campaign_config: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.campaign_config, Unset):
            campaign_config = self.campaign_config.to_dict() if self.campaign_config else None

        campaign_config_send: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.campaign_config_send, Unset):
            campaign_config_send = self.campaign_config_send.to_dict() if self.campaign_config_send else None

        campaign_send_stat: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.campaign_send_stat, Unset):
            campaign_send_stat = self.campaign_send_stat.to_dict() if self.campaign_send_stat else None

        template = self.template
        audience = self.audience
        list_segment: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.list_segment, Unset):
            list_segment = self.list_segment.to_dict() if self.list_segment else None

        send_to = self.send_to
        created_at: Union[Unset, None, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat() if self.created_at else None

        updated_at: Union[Unset, None, str] = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat() if self.updated_at else None

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if context is not UNSET:
            field_dict["@context"] = context
        if id is not UNSET:
            field_dict["@id"] = id
        if type is not UNSET:
            field_dict["@type"] = type
        if title is not UNSET:
            field_dict["title"] = title
        if status is not UNSET:
            field_dict["status"] = status
        if template_html is not UNSET:
            field_dict["template_html"] = template_html
        if template_thumbnail is not UNSET:
            field_dict["template_thumbnail"] = template_thumbnail
        if email_config is not UNSET:
            field_dict["email_config"] = email_config
        if campaign_config is not UNSET:
            field_dict["campaign_config"] = campaign_config
        if campaign_config_send is not UNSET:
            field_dict["campaign_config_send"] = campaign_config_send
        if campaign_send_stat is not UNSET:
            field_dict["campaign_send_stat"] = campaign_send_stat
        if template is not UNSET:
            field_dict["template"] = template
        if audience is not UNSET:
            field_dict["audience"] = audience
        if list_segment is not UNSET:
            field_dict["list_segment"] = list_segment
        if send_to is not UNSET:
            field_dict["send_to"] = send_to
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.campaign_config_jsonld_campaign_read import CampaignConfigJsonldCampaignRead
        from ..models.campaign_config_send_jsonld_campaign_read import CampaignConfigSendJsonldCampaignRead
        from ..models.campaign_jsonld_campaign_read_context_type_1 import CampaignJsonldCampaignReadContextType1
        from ..models.campaign_send_stat_jsonld_campaign_read import CampaignSendStatJsonldCampaignRead
        from ..models.email_config_jsonld_campaign_read import EmailConfigJsonldCampaignRead
        from ..models.list_segment_jsonld_campaign_read import ListSegmentJsonldCampaignRead

        d = src_dict.copy()

        def _parse_context(data: object) -> Union["CampaignJsonldCampaignReadContextType1", Unset, str]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                _context_type_1 = data
                context_type_1: Union[Unset, CampaignJsonldCampaignReadContextType1]
                if isinstance(_context_type_1, Unset):
                    context_type_1 = UNSET
                else:
                    context_type_1 = CampaignJsonldCampaignReadContextType1.from_dict(_context_type_1)

                return context_type_1
            except:  # noqa: E722
                pass
            return cast(Union["CampaignJsonldCampaignReadContextType1", Unset, str], data)

        context = _parse_context(d.pop("@context", UNSET))

        id = d.pop("@id", UNSET)

        type = d.pop("@type", UNSET)

        title = d.pop("title", UNSET)

        status = d.pop("status", UNSET)

        template_html = d.pop("template_html", UNSET)

        template_thumbnail = d.pop("template_thumbnail", UNSET)

        _email_config = d.pop("email_config", UNSET)
        email_config: Union[Unset, None, EmailConfigJsonldCampaignRead]
        if _email_config is None:
            email_config = None
        elif isinstance(_email_config, Unset):
            email_config = UNSET
        else:
            email_config = EmailConfigJsonldCampaignRead.from_dict(_email_config)

        _campaign_config = d.pop("campaign_config", UNSET)
        campaign_config: Union[Unset, None, CampaignConfigJsonldCampaignRead]
        if _campaign_config is None:
            campaign_config = None
        elif isinstance(_campaign_config, Unset):
            campaign_config = UNSET
        else:
            campaign_config = CampaignConfigJsonldCampaignRead.from_dict(_campaign_config)

        _campaign_config_send = d.pop("campaign_config_send", UNSET)
        campaign_config_send: Union[Unset, None, CampaignConfigSendJsonldCampaignRead]
        if _campaign_config_send is None:
            campaign_config_send = None
        elif isinstance(_campaign_config_send, Unset):
            campaign_config_send = UNSET
        else:
            campaign_config_send = CampaignConfigSendJsonldCampaignRead.from_dict(_campaign_config_send)

        _campaign_send_stat = d.pop("campaign_send_stat", UNSET)
        campaign_send_stat: Union[Unset, None, CampaignSendStatJsonldCampaignRead]
        if _campaign_send_stat is None:
            campaign_send_stat = None
        elif isinstance(_campaign_send_stat, Unset):
            campaign_send_stat = UNSET
        else:
            campaign_send_stat = CampaignSendStatJsonldCampaignRead.from_dict(_campaign_send_stat)

        template = d.pop("template", UNSET)

        audience = d.pop("audience", UNSET)

        _list_segment = d.pop("list_segment", UNSET)
        list_segment: Union[Unset, None, ListSegmentJsonldCampaignRead]
        if _list_segment is None:
            list_segment = None
        elif isinstance(_list_segment, Unset):
            list_segment = UNSET
        else:
            list_segment = ListSegmentJsonldCampaignRead.from_dict(_list_segment)

        send_to = d.pop("send_to", UNSET)

        _created_at = d.pop("created_at", UNSET)
        created_at: Union[Unset, None, datetime.datetime]
        if _created_at is None:
            created_at = None
        elif isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        _updated_at = d.pop("updated_at", UNSET)
        updated_at: Union[Unset, None, datetime.datetime]
        if _updated_at is None:
            updated_at = None
        elif isinstance(_updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = isoparse(_updated_at)

        campaign_jsonld_campaign_read = cls(
            context=context,
            id=id,
            type=type,
            title=title,
            status=status,
            template_html=template_html,
            template_thumbnail=template_thumbnail,
            email_config=email_config,
            campaign_config=campaign_config,
            campaign_config_send=campaign_config_send,
            campaign_send_stat=campaign_send_stat,
            template=template,
            audience=audience,
            list_segment=list_segment,
            send_to=send_to,
            created_at=created_at,
            updated_at=updated_at,
        )

        campaign_jsonld_campaign_read.additional_properties = d
        return campaign_jsonld_campaign_read

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
