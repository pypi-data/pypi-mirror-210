import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Type, TypeVar, Union, cast

import attr
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.list_segment_jsonld_campaign_read_context_type_1 import ListSegmentJsonldCampaignReadContextType1


T = TypeVar("T", bound="ListSegmentJsonldCampaignRead")


@attr.s(auto_attribs=True)
class ListSegmentJsonldCampaignRead:
    """
    Attributes:
        context (Union['ListSegmentJsonldCampaignReadContextType1', Unset, str]):
        id (Union[Unset, str]):
        type (Union[Unset, str]):
        name (Optional[datetime.datetime]): Segment name Example: My awesome segmentation!.
        description (Union[Unset, None, str]): Segment description Example: Custom segmentation description.
    """

    name: Optional[datetime.datetime]
    context: Union["ListSegmentJsonldCampaignReadContextType1", Unset, str] = UNSET
    id: Union[Unset, str] = UNSET
    type: Union[Unset, str] = UNSET
    description: Union[Unset, None, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.list_segment_jsonld_campaign_read_context_type_1 import ListSegmentJsonldCampaignReadContextType1

        context: Union[Dict[str, Any], Unset, str]
        if isinstance(self.context, Unset):
            context = UNSET

        elif isinstance(self.context, ListSegmentJsonldCampaignReadContextType1):
            context = UNSET
            if not isinstance(self.context, Unset):
                context = self.context.to_dict()

        else:
            context = self.context

        id = self.id
        type = self.type
        name = self.name.isoformat() if self.name else None

        description = self.description

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if context is not UNSET:
            field_dict["@context"] = context
        if id is not UNSET:
            field_dict["@id"] = id
        if type is not UNSET:
            field_dict["@type"] = type
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.list_segment_jsonld_campaign_read_context_type_1 import ListSegmentJsonldCampaignReadContextType1

        d = src_dict.copy()

        def _parse_context(data: object) -> Union["ListSegmentJsonldCampaignReadContextType1", Unset, str]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                _context_type_1 = data
                context_type_1: Union[Unset, ListSegmentJsonldCampaignReadContextType1]
                if isinstance(_context_type_1, Unset):
                    context_type_1 = UNSET
                else:
                    context_type_1 = ListSegmentJsonldCampaignReadContextType1.from_dict(_context_type_1)

                return context_type_1
            except:  # noqa: E722
                pass
            return cast(Union["ListSegmentJsonldCampaignReadContextType1", Unset, str], data)

        context = _parse_context(d.pop("@context", UNSET))

        id = d.pop("@id", UNSET)

        type = d.pop("@type", UNSET)

        _name = d.pop("name")
        name: Optional[datetime.datetime]
        if _name is None:
            name = None
        else:
            name = isoparse(_name)

        description = d.pop("description", UNSET)

        list_segment_jsonld_campaign_read = cls(
            context=context,
            id=id,
            type=type,
            name=name,
            description=description,
        )

        list_segment_jsonld_campaign_read.additional_properties = d
        return list_segment_jsonld_campaign_read

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
