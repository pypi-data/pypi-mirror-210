from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="TreatmentPurposeAudienceRead")


@attr.s(auto_attribs=True)
class TreatmentPurposeAudienceRead:
    """
    Attributes:
        name (Union[Unset, None, str]): Name Example: I accept the sending of commercial communications and / or
            Newsletters.
        description (Union[Unset, None, str]): Description Example: Commercial newsletters.
        custom (Union[Unset, None, bool]): Is custom treatment purpose
    """

    name: Union[Unset, None, str] = UNSET
    description: Union[Unset, None, str] = UNSET
    custom: Union[Unset, None, bool] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        description = self.description
        custom = self.custom

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if custom is not UNSET:
            field_dict["custom"] = custom

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name", UNSET)

        description = d.pop("description", UNSET)

        custom = d.pop("custom", UNSET)

        treatment_purpose_audience_read = cls(
            name=name,
            description=description,
            custom=custom,
        )

        treatment_purpose_audience_read.additional_properties = d
        return treatment_purpose_audience_read

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
