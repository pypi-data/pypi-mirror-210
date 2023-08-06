from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetAutomationTriggerCollectionResponse200Hydraview")


@attr.s(auto_attribs=True)
class GetAutomationTriggerCollectionResponse200Hydraview:
    """
    Attributes:
        id (Union[Unset, str]):
        type (Union[Unset, str]):
        hydrafirst (Union[Unset, str]):
        hydralast (Union[Unset, str]):
        hydraprevious (Union[Unset, str]):
        hydranext (Union[Unset, str]):
    """

    id: Union[Unset, str] = UNSET
    type: Union[Unset, str] = UNSET
    hydrafirst: Union[Unset, str] = UNSET
    hydralast: Union[Unset, str] = UNSET
    hydraprevious: Union[Unset, str] = UNSET
    hydranext: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        type = self.type
        hydrafirst = self.hydrafirst
        hydralast = self.hydralast
        hydraprevious = self.hydraprevious
        hydranext = self.hydranext

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["@id"] = id
        if type is not UNSET:
            field_dict["@type"] = type
        if hydrafirst is not UNSET:
            field_dict["hydra:first"] = hydrafirst
        if hydralast is not UNSET:
            field_dict["hydra:last"] = hydralast
        if hydraprevious is not UNSET:
            field_dict["hydra:previous"] = hydraprevious
        if hydranext is not UNSET:
            field_dict["hydra:next"] = hydranext

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("@id", UNSET)

        type = d.pop("@type", UNSET)

        hydrafirst = d.pop("hydra:first", UNSET)

        hydralast = d.pop("hydra:last", UNSET)

        hydraprevious = d.pop("hydra:previous", UNSET)

        hydranext = d.pop("hydra:next", UNSET)

        get_automation_trigger_collection_response_200_hydraview = cls(
            id=id,
            type=type,
            hydrafirst=hydrafirst,
            hydralast=hydralast,
            hydraprevious=hydraprevious,
            hydranext=hydranext,
        )

        get_automation_trigger_collection_response_200_hydraview.additional_properties = d
        return get_automation_trigger_collection_response_200_hydraview

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
