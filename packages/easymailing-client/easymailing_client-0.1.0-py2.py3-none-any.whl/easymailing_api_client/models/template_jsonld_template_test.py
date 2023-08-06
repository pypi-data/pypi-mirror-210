from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.template_jsonld_template_test_context_type_1 import TemplateJsonldTemplateTestContextType1


T = TypeVar("T", bound="TemplateJsonldTemplateTest")


@attr.s(auto_attribs=True)
class TemplateJsonldTemplateTest:
    """
    Attributes:
        context (Union['TemplateJsonldTemplateTestContextType1', Unset, str]):
        id (Union[Unset, str]):
        type (Union[Unset, str]):
        title (Union[Unset, None, str]): Template title Example: My awesome template!.
        content (Union[Unset, None, str]): The template HTML Example: <html><body><p>My awesome
            template!</p></body</html>.
    """

    context: Union["TemplateJsonldTemplateTestContextType1", Unset, str] = UNSET
    id: Union[Unset, str] = UNSET
    type: Union[Unset, str] = UNSET
    title: Union[Unset, None, str] = UNSET
    content: Union[Unset, None, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.template_jsonld_template_test_context_type_1 import TemplateJsonldTemplateTestContextType1

        context: Union[Dict[str, Any], Unset, str]
        if isinstance(self.context, Unset):
            context = UNSET

        elif isinstance(self.context, TemplateJsonldTemplateTestContextType1):
            context = UNSET
            if not isinstance(self.context, Unset):
                context = self.context.to_dict()

        else:
            context = self.context

        id = self.id
        type = self.type
        title = self.title
        content = self.content

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if context is not UNSET:
            field_dict["@context"] = context
        if id is not UNSET:
            field_dict["@id"] = id
        if type is not UNSET:
            field_dict["@type"] = type
        if title is not UNSET:
            field_dict["title"] = title
        if content is not UNSET:
            field_dict["content"] = content

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.template_jsonld_template_test_context_type_1 import TemplateJsonldTemplateTestContextType1

        d = src_dict.copy()

        def _parse_context(data: object) -> Union["TemplateJsonldTemplateTestContextType1", Unset, str]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                _context_type_1 = data
                context_type_1: Union[Unset, TemplateJsonldTemplateTestContextType1]
                if isinstance(_context_type_1, Unset):
                    context_type_1 = UNSET
                else:
                    context_type_1 = TemplateJsonldTemplateTestContextType1.from_dict(_context_type_1)

                return context_type_1
            except:  # noqa: E722
                pass
            return cast(Union["TemplateJsonldTemplateTestContextType1", Unset, str], data)

        context = _parse_context(d.pop("@context", UNSET))

        id = d.pop("@id", UNSET)

        type = d.pop("@type", UNSET)

        title = d.pop("title", UNSET)

        content = d.pop("content", UNSET)

        template_jsonld_template_test = cls(
            context=context,
            id=id,
            type=type,
            title=title,
            content=content,
        )

        template_jsonld_template_test.additional_properties = d
        return template_jsonld_template_test

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
