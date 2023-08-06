from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.custom_field_jsonld_contact_write_context_type_1 import CustomFieldJsonldContactWriteContextType1


T = TypeVar("T", bound="CustomFieldJsonldContactWrite")


@attr.s(auto_attribs=True)
class CustomFieldJsonldContactWrite:
    """
    Attributes:
        list_field (str): Listfield Example: /list_fields/0df14405-90ff-4287-b3e4-ef088901ee6f.
        context (Union['CustomFieldJsonldContactWriteContextType1', Unset, str]):
        id (Union[Unset, str]):
        type (Union[Unset, str]):
        value (Union[Unset, Any]):
    """

    list_field: str
    context: Union["CustomFieldJsonldContactWriteContextType1", Unset, str] = UNSET
    id: Union[Unset, str] = UNSET
    type: Union[Unset, str] = UNSET
    value: Union[Unset, Any] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.custom_field_jsonld_contact_write_context_type_1 import CustomFieldJsonldContactWriteContextType1

        list_field = self.list_field
        context: Union[Dict[str, Any], Unset, str]
        if isinstance(self.context, Unset):
            context = UNSET

        elif isinstance(self.context, CustomFieldJsonldContactWriteContextType1):
            context = UNSET
            if not isinstance(self.context, Unset):
                context = self.context.to_dict()

        else:
            context = self.context

        id = self.id
        type = self.type
        value = self.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "list_field": list_field,
            }
        )
        if context is not UNSET:
            field_dict["@context"] = context
        if id is not UNSET:
            field_dict["@id"] = id
        if type is not UNSET:
            field_dict["@type"] = type
        if value is not UNSET:
            field_dict["value"] = value

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.custom_field_jsonld_contact_write_context_type_1 import CustomFieldJsonldContactWriteContextType1

        d = src_dict.copy()
        list_field = d.pop("list_field")

        def _parse_context(data: object) -> Union["CustomFieldJsonldContactWriteContextType1", Unset, str]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                _context_type_1 = data
                context_type_1: Union[Unset, CustomFieldJsonldContactWriteContextType1]
                if isinstance(_context_type_1, Unset):
                    context_type_1 = UNSET
                else:
                    context_type_1 = CustomFieldJsonldContactWriteContextType1.from_dict(_context_type_1)

                return context_type_1
            except:  # noqa: E722
                pass
            return cast(Union["CustomFieldJsonldContactWriteContextType1", Unset, str], data)

        context = _parse_context(d.pop("@context", UNSET))

        id = d.pop("@id", UNSET)

        type = d.pop("@type", UNSET)

        value = d.pop("value", UNSET)

        custom_field_jsonld_contact_write = cls(
            list_field=list_field,
            context=context,
            id=id,
            type=type,
            value=value,
        )

        custom_field_jsonld_contact_write.additional_properties = d
        return custom_field_jsonld_contact_write

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
