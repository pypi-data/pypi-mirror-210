import datetime
from typing import Any, Dict, List, Optional, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="ListSegmentCampaignRead")


@attr.s(auto_attribs=True)
class ListSegmentCampaignRead:
    """
    Attributes:
        name (Optional[datetime.datetime]): Segment name Example: My awesome segmentation!.
        description (Union[Unset, None, str]): Segment description Example: Custom segmentation description.
    """

    name: Optional[datetime.datetime]
    description: Union[Unset, None, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name.isoformat() if self.name else None

        description = self.description

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _name = d.pop("name")
        name: Optional[datetime.datetime]
        if _name is None:
            name = None
        else:
            name = isoparse(_name)

        description = d.pop("description", UNSET)

        list_segment_campaign_read = cls(
            name=name,
            description=description,
        )

        list_segment_campaign_read.additional_properties = d
        return list_segment_campaign_read

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
