from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.list_field_list_field_input_jsonld_list_field_write_context_type_1 import (
        ListFieldListFieldInputJsonldListFieldWriteContextType1,
    )


T = TypeVar("T", bound="ListFieldListFieldInputJsonldListFieldWrite")


@attr.s(auto_attribs=True)
class ListFieldListFieldInputJsonldListFieldWrite:
    """
    Attributes:
        context (Union['ListFieldListFieldInputJsonldListFieldWriteContextType1', Unset, str]):
        id (Union[Unset, str]):
        type (Union[Unset, str]):
        tag (Union[Unset, str]): Custom field TAG
        template_tag (Union[Unset, str]): Custom field TAG for use in templates
        public (Union[Unset, bool]): Public
        required (Union[Unset, bool]): Required
        type (Union[Unset, str]): Value
    """

    context: Union["ListFieldListFieldInputJsonldListFieldWriteContextType1", Unset, str] = UNSET
    id: Union[Unset, str] = UNSET
    type: Union[Unset, str] = UNSET
    tag: Union[Unset, str] = UNSET
    template_tag: Union[Unset, str] = UNSET
    public: Union[Unset, bool] = UNSET
    required: Union[Unset, bool] = UNSET
    type: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.list_field_list_field_input_jsonld_list_field_write_context_type_1 import (
            ListFieldListFieldInputJsonldListFieldWriteContextType1,
        )

        context: Union[Dict[str, Any], Unset, str]
        if isinstance(self.context, Unset):
            context = UNSET

        elif isinstance(self.context, ListFieldListFieldInputJsonldListFieldWriteContextType1):
            context = UNSET
            if not isinstance(self.context, Unset):
                context = self.context.to_dict()

        else:
            context = self.context

        id = self.id
        type = self.type
        tag = self.tag
        template_tag = self.template_tag
        public = self.public
        required = self.required
        type = self.type

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if context is not UNSET:
            field_dict["@context"] = context
        if id is not UNSET:
            field_dict["@id"] = id
        if type is not UNSET:
            field_dict["@type"] = type
        if tag is not UNSET:
            field_dict["tag"] = tag
        if template_tag is not UNSET:
            field_dict["template_tag"] = template_tag
        if public is not UNSET:
            field_dict["public"] = public
        if required is not UNSET:
            field_dict["required"] = required
        if type is not UNSET:
            field_dict["type"] = type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.list_field_list_field_input_jsonld_list_field_write_context_type_1 import (
            ListFieldListFieldInputJsonldListFieldWriteContextType1,
        )

        d = src_dict.copy()

        def _parse_context(
            data: object,
        ) -> Union["ListFieldListFieldInputJsonldListFieldWriteContextType1", Unset, str]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                _context_type_1 = data
                context_type_1: Union[Unset, ListFieldListFieldInputJsonldListFieldWriteContextType1]
                if isinstance(_context_type_1, Unset):
                    context_type_1 = UNSET
                else:
                    context_type_1 = ListFieldListFieldInputJsonldListFieldWriteContextType1.from_dict(_context_type_1)

                return context_type_1
            except:  # noqa: E722
                pass
            return cast(Union["ListFieldListFieldInputJsonldListFieldWriteContextType1", Unset, str], data)

        context = _parse_context(d.pop("@context", UNSET))

        id = d.pop("@id", UNSET)

        type = d.pop("@type", UNSET)

        tag = d.pop("tag", UNSET)

        template_tag = d.pop("template_tag", UNSET)

        public = d.pop("public", UNSET)

        required = d.pop("required", UNSET)

        type = d.pop("type", UNSET)

        list_field_list_field_input_jsonld_list_field_write = cls(
            context=context,
            id=id,
            type=type,
            tag=tag,
            template_tag=template_tag,
            public=public,
            required=required,
        )

        list_field_list_field_input_jsonld_list_field_write.additional_properties = d
        return list_field_list_field_input_jsonld_list_field_write

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
