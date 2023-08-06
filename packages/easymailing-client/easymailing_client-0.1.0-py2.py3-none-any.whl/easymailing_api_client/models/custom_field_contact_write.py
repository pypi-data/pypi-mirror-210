from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="CustomFieldContactWrite")


@attr.s(auto_attribs=True)
class CustomFieldContactWrite:
    """
    Attributes:
        list_field (str): Listfield Example: /list_fields/0df14405-90ff-4287-b3e4-ef088901ee6f.
        value (Union[Unset, Any]):
    """

    list_field: str
    value: Union[Unset, Any] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        list_field = self.list_field
        value = self.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "list_field": list_field,
            }
        )
        if value is not UNSET:
            field_dict["value"] = value

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        list_field = d.pop("list_field")

        value = d.pop("value", UNSET)

        custom_field_contact_write = cls(
            list_field=list_field,
            value=value,
        )

        custom_field_contact_write.additional_properties = d
        return custom_field_contact_write

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
