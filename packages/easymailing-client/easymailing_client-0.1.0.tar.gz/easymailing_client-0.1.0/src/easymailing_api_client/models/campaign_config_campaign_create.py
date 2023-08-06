from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="CampaignConfigCampaignCreate")


@attr.s(auto_attribs=True)
class CampaignConfigCampaignCreate:
    """
    Attributes:
        track_opens (Union[Unset, bool]): Track opens in campaign Example: True.
        track_clicks (Union[Unset, bool]): Track clicks in campaign Example: True.
        use_conversations (Union[Unset, bool]): Use conversations in campaign Example: True.
        public (Union[Unset, bool]): Publish the campaign in archive page Example: True.
        google_analytics_tag (Union[Unset, None, str]):
        track_google_analytics (Union[Unset, bool]):
    """

    track_opens: Union[Unset, bool] = UNSET
    track_clicks: Union[Unset, bool] = UNSET
    use_conversations: Union[Unset, bool] = UNSET
    public: Union[Unset, bool] = UNSET
    google_analytics_tag: Union[Unset, None, str] = UNSET
    track_google_analytics: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        track_opens = self.track_opens
        track_clicks = self.track_clicks
        use_conversations = self.use_conversations
        public = self.public
        google_analytics_tag = self.google_analytics_tag
        track_google_analytics = self.track_google_analytics

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if track_opens is not UNSET:
            field_dict["track_opens"] = track_opens
        if track_clicks is not UNSET:
            field_dict["track_clicks"] = track_clicks
        if use_conversations is not UNSET:
            field_dict["use_conversations"] = use_conversations
        if public is not UNSET:
            field_dict["public"] = public
        if google_analytics_tag is not UNSET:
            field_dict["google_analytics_tag"] = google_analytics_tag
        if track_google_analytics is not UNSET:
            field_dict["track_google_analytics"] = track_google_analytics

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        track_opens = d.pop("track_opens", UNSET)

        track_clicks = d.pop("track_clicks", UNSET)

        use_conversations = d.pop("use_conversations", UNSET)

        public = d.pop("public", UNSET)

        google_analytics_tag = d.pop("google_analytics_tag", UNSET)

        track_google_analytics = d.pop("track_google_analytics", UNSET)

        campaign_config_campaign_create = cls(
            track_opens=track_opens,
            track_clicks=track_clicks,
            use_conversations=use_conversations,
            public=public,
            google_analytics_tag=google_analytics_tag,
            track_google_analytics=track_google_analytics,
        )

        campaign_config_campaign_create.additional_properties = d
        return campaign_config_campaign_create

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
