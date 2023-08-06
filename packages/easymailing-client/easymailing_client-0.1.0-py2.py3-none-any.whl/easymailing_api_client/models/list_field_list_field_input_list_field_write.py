from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="ListFieldListFieldInputListFieldWrite")


@attr.s(auto_attribs=True)
class ListFieldListFieldInputListFieldWrite:
    """
    Attributes:
        tag (Union[Unset, str]): Custom field TAG
        template_tag (Union[Unset, str]): Custom field TAG for use in templates
        public (Union[Unset, bool]): Public
        required (Union[Unset, bool]): Required
        type (Union[Unset, str]): Value
    """

    tag: Union[Unset, str] = UNSET
    template_tag: Union[Unset, str] = UNSET
    public: Union[Unset, bool] = UNSET
    required: Union[Unset, bool] = UNSET
    type: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        tag = self.tag
        template_tag = self.template_tag
        public = self.public
        required = self.required
        type = self.type

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
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
        d = src_dict.copy()
        tag = d.pop("tag", UNSET)

        template_tag = d.pop("template_tag", UNSET)

        public = d.pop("public", UNSET)

        required = d.pop("required", UNSET)

        type = d.pop("type", UNSET)

        list_field_list_field_input_list_field_write = cls(
            tag=tag,
            template_tag=template_tag,
            public=public,
            required=required,
            type=type,
        )

        list_field_list_field_input_list_field_write.additional_properties = d
        return list_field_list_field_input_list_field_write

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
