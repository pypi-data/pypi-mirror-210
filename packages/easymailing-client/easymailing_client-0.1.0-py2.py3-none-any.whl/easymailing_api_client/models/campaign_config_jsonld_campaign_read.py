from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.campaign_config_jsonld_campaign_read_context_type_1 import (
        CampaignConfigJsonldCampaignReadContextType1,
    )


T = TypeVar("T", bound="CampaignConfigJsonldCampaignRead")


@attr.s(auto_attribs=True)
class CampaignConfigJsonldCampaignRead:
    """
    Attributes:
        id (Union[Unset, str]):
        type (Union[Unset, str]):
        context (Union['CampaignConfigJsonldCampaignReadContextType1', Unset, str]):
        track_opens (Union[Unset, None, bool]):
        track_clicks (Union[Unset, None, bool]):
        track_google_analytics (Union[Unset, None, bool]):
        google_analytics_tag (Union[Unset, None, str]):
        use_conversations (Union[Unset, None, bool]):
        public (Union[Unset, None, bool]):
    """

    id: Union[Unset, str] = UNSET
    type: Union[Unset, str] = UNSET
    context: Union["CampaignConfigJsonldCampaignReadContextType1", Unset, str] = UNSET
    track_opens: Union[Unset, None, bool] = UNSET
    track_clicks: Union[Unset, None, bool] = UNSET
    track_google_analytics: Union[Unset, None, bool] = UNSET
    google_analytics_tag: Union[Unset, None, str] = UNSET
    use_conversations: Union[Unset, None, bool] = UNSET
    public: Union[Unset, None, bool] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.campaign_config_jsonld_campaign_read_context_type_1 import (
            CampaignConfigJsonldCampaignReadContextType1,
        )

        id = self.id
        type = self.type
        context: Union[Dict[str, Any], Unset, str]
        if isinstance(self.context, Unset):
            context = UNSET

        elif isinstance(self.context, CampaignConfigJsonldCampaignReadContextType1):
            context = UNSET
            if not isinstance(self.context, Unset):
                context = self.context.to_dict()

        else:
            context = self.context

        track_opens = self.track_opens
        track_clicks = self.track_clicks
        track_google_analytics = self.track_google_analytics
        google_analytics_tag = self.google_analytics_tag
        use_conversations = self.use_conversations
        public = self.public

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["@id"] = id
        if type is not UNSET:
            field_dict["@type"] = type
        if context is not UNSET:
            field_dict["@context"] = context
        if track_opens is not UNSET:
            field_dict["track_opens"] = track_opens
        if track_clicks is not UNSET:
            field_dict["track_clicks"] = track_clicks
        if track_google_analytics is not UNSET:
            field_dict["track_google_analytics"] = track_google_analytics
        if google_analytics_tag is not UNSET:
            field_dict["google_analytics_tag"] = google_analytics_tag
        if use_conversations is not UNSET:
            field_dict["use_conversations"] = use_conversations
        if public is not UNSET:
            field_dict["public"] = public

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.campaign_config_jsonld_campaign_read_context_type_1 import (
            CampaignConfigJsonldCampaignReadContextType1,
        )

        d = src_dict.copy()
        id = d.pop("@id", UNSET)

        type = d.pop("@type", UNSET)

        def _parse_context(data: object) -> Union["CampaignConfigJsonldCampaignReadContextType1", Unset, str]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                _context_type_1 = data
                context_type_1: Union[Unset, CampaignConfigJsonldCampaignReadContextType1]
                if isinstance(_context_type_1, Unset):
                    context_type_1 = UNSET
                else:
                    context_type_1 = CampaignConfigJsonldCampaignReadContextType1.from_dict(_context_type_1)

                return context_type_1
            except:  # noqa: E722
                pass
            return cast(Union["CampaignConfigJsonldCampaignReadContextType1", Unset, str], data)

        context = _parse_context(d.pop("@context", UNSET))

        track_opens = d.pop("track_opens", UNSET)

        track_clicks = d.pop("track_clicks", UNSET)

        track_google_analytics = d.pop("track_google_analytics", UNSET)

        google_analytics_tag = d.pop("google_analytics_tag", UNSET)

        use_conversations = d.pop("use_conversations", UNSET)

        public = d.pop("public", UNSET)

        campaign_config_jsonld_campaign_read = cls(
            id=id,
            type=type,
            context=context,
            track_opens=track_opens,
            track_clicks=track_clicks,
            track_google_analytics=track_google_analytics,
            google_analytics_tag=google_analytics_tag,
            use_conversations=use_conversations,
            public=public,
        )

        campaign_config_jsonld_campaign_read.additional_properties = d
        return campaign_config_jsonld_campaign_read

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
