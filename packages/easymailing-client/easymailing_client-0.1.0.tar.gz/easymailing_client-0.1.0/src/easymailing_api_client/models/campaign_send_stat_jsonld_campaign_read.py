from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.campaign_send_stat_jsonld_campaign_read_context_type_1 import (
        CampaignSendStatJsonldCampaignReadContextType1,
    )


T = TypeVar("T", bound="CampaignSendStatJsonldCampaignRead")


@attr.s(auto_attribs=True)
class CampaignSendStatJsonldCampaignRead:
    """
    Attributes:
        id (Union[Unset, str]):
        type (Union[Unset, str]):
        context (Union['CampaignSendStatJsonldCampaignReadContextType1', Unset, str]):
        sent (Union[Unset, None, int]): Emails sent Example: 100.
        delivered (Union[Unset, None, int]): Emails delivered Example: 90.
        clicks (Union[Unset, None, int]): Total clicks Example: 10.
        unique_clicks (Union[Unset, None, int]): Unique clicks Example: 5.
        opens (Union[Unset, None, int]): Total opens Example: 40.
        unique_opens (Union[Unset, None, int]): Unique opens Example: 20.
        complaints (Union[Unset, None, int]): Complaints received
        soft_bounces (Union[Unset, None, int]): Soft bounces Example: 2.
        hard_bounces (Union[Unset, None, int]): Hard bounces Example: 8.
        unsubscriptions (Union[Unset, None, int]): Unsubscriptions Example: 5.
    """

    id: Union[Unset, str] = UNSET
    type: Union[Unset, str] = UNSET
    context: Union["CampaignSendStatJsonldCampaignReadContextType1", Unset, str] = UNSET
    sent: Union[Unset, None, int] = UNSET
    delivered: Union[Unset, None, int] = UNSET
    clicks: Union[Unset, None, int] = UNSET
    unique_clicks: Union[Unset, None, int] = UNSET
    opens: Union[Unset, None, int] = UNSET
    unique_opens: Union[Unset, None, int] = UNSET
    complaints: Union[Unset, None, int] = UNSET
    soft_bounces: Union[Unset, None, int] = UNSET
    hard_bounces: Union[Unset, None, int] = UNSET
    unsubscriptions: Union[Unset, None, int] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.campaign_send_stat_jsonld_campaign_read_context_type_1 import (
            CampaignSendStatJsonldCampaignReadContextType1,
        )

        id = self.id
        type = self.type
        context: Union[Dict[str, Any], Unset, str]
        if isinstance(self.context, Unset):
            context = UNSET

        elif isinstance(self.context, CampaignSendStatJsonldCampaignReadContextType1):
            context = UNSET
            if not isinstance(self.context, Unset):
                context = self.context.to_dict()

        else:
            context = self.context

        sent = self.sent
        delivered = self.delivered
        clicks = self.clicks
        unique_clicks = self.unique_clicks
        opens = self.opens
        unique_opens = self.unique_opens
        complaints = self.complaints
        soft_bounces = self.soft_bounces
        hard_bounces = self.hard_bounces
        unsubscriptions = self.unsubscriptions

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["@id"] = id
        if type is not UNSET:
            field_dict["@type"] = type
        if context is not UNSET:
            field_dict["@context"] = context
        if sent is not UNSET:
            field_dict["sent"] = sent
        if delivered is not UNSET:
            field_dict["delivered"] = delivered
        if clicks is not UNSET:
            field_dict["clicks"] = clicks
        if unique_clicks is not UNSET:
            field_dict["unique_clicks"] = unique_clicks
        if opens is not UNSET:
            field_dict["opens"] = opens
        if unique_opens is not UNSET:
            field_dict["unique_opens"] = unique_opens
        if complaints is not UNSET:
            field_dict["complaints"] = complaints
        if soft_bounces is not UNSET:
            field_dict["soft_bounces"] = soft_bounces
        if hard_bounces is not UNSET:
            field_dict["hard_bounces"] = hard_bounces
        if unsubscriptions is not UNSET:
            field_dict["unsubscriptions"] = unsubscriptions

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.campaign_send_stat_jsonld_campaign_read_context_type_1 import (
            CampaignSendStatJsonldCampaignReadContextType1,
        )

        d = src_dict.copy()
        id = d.pop("@id", UNSET)

        type = d.pop("@type", UNSET)

        def _parse_context(data: object) -> Union["CampaignSendStatJsonldCampaignReadContextType1", Unset, str]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                _context_type_1 = data
                context_type_1: Union[Unset, CampaignSendStatJsonldCampaignReadContextType1]
                if isinstance(_context_type_1, Unset):
                    context_type_1 = UNSET
                else:
                    context_type_1 = CampaignSendStatJsonldCampaignReadContextType1.from_dict(_context_type_1)

                return context_type_1
            except:  # noqa: E722
                pass
            return cast(Union["CampaignSendStatJsonldCampaignReadContextType1", Unset, str], data)

        context = _parse_context(d.pop("@context", UNSET))

        sent = d.pop("sent", UNSET)

        delivered = d.pop("delivered", UNSET)

        clicks = d.pop("clicks", UNSET)

        unique_clicks = d.pop("unique_clicks", UNSET)

        opens = d.pop("opens", UNSET)

        unique_opens = d.pop("unique_opens", UNSET)

        complaints = d.pop("complaints", UNSET)

        soft_bounces = d.pop("soft_bounces", UNSET)

        hard_bounces = d.pop("hard_bounces", UNSET)

        unsubscriptions = d.pop("unsubscriptions", UNSET)

        campaign_send_stat_jsonld_campaign_read = cls(
            id=id,
            type=type,
            context=context,
            sent=sent,
            delivered=delivered,
            clicks=clicks,
            unique_clicks=unique_clicks,
            opens=opens,
            unique_opens=unique_opens,
            complaints=complaints,
            soft_bounces=soft_bounces,
            hard_bounces=hard_bounces,
            unsubscriptions=unsubscriptions,
        )

        campaign_send_stat_jsonld_campaign_read.additional_properties = d
        return campaign_send_stat_jsonld_campaign_read

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
