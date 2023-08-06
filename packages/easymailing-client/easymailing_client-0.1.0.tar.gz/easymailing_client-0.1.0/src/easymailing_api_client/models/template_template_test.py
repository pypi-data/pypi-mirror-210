from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="TemplateTemplateTest")


@attr.s(auto_attribs=True)
class TemplateTemplateTest:
    """
    Attributes:
        title (Union[Unset, None, str]): Template title Example: My awesome template!.
        content (Union[Unset, None, str]): The template HTML Example: <html><body><p>My awesome
            template!</p></body</html>.
    """

    title: Union[Unset, None, str] = UNSET
    content: Union[Unset, None, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        title = self.title
        content = self.content

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if title is not UNSET:
            field_dict["title"] = title
        if content is not UNSET:
            field_dict["content"] = content

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        title = d.pop("title", UNSET)

        content = d.pop("content", UNSET)

        template_template_test = cls(
            title=title,
            content=content,
        )

        template_template_test.additional_properties = d
        return template_template_test

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
