from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetTemplateCollectionResponse200HydrasearchHydramappingItem")


@attr.s(auto_attribs=True)
class GetTemplateCollectionResponse200HydrasearchHydramappingItem:
    """
    Attributes:
        type (Union[Unset, str]):
        variable (Union[Unset, str]):
        property_ (Union[Unset, None, str]):
        required (Union[Unset, bool]):
    """

    type: Union[Unset, str] = UNSET
    variable: Union[Unset, str] = UNSET
    property_: Union[Unset, None, str] = UNSET
    required: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        type = self.type
        variable = self.variable
        property_ = self.property_
        required = self.required

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if type is not UNSET:
            field_dict["@type"] = type
        if variable is not UNSET:
            field_dict["variable"] = variable
        if property_ is not UNSET:
            field_dict["property"] = property_
        if required is not UNSET:
            field_dict["required"] = required

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        type = d.pop("@type", UNSET)

        variable = d.pop("variable", UNSET)

        property_ = d.pop("property", UNSET)

        required = d.pop("required", UNSET)

        get_template_collection_response_200_hydrasearch_hydramapping_item = cls(
            type=type,
            variable=variable,
            property_=property_,
            required=required,
        )

        get_template_collection_response_200_hydrasearch_hydramapping_item.additional_properties = d
        return get_template_collection_response_200_hydrasearch_hydramapping_item

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
