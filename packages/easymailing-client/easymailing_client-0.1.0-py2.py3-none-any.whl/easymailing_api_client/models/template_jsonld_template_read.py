import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

import attr
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.template_jsonld_template_read_context_type_1 import TemplateJsonldTemplateReadContextType1


T = TypeVar("T", bound="TemplateJsonldTemplateRead")


@attr.s(auto_attribs=True)
class TemplateJsonldTemplateRead:
    """
    Attributes:
        context (Union['TemplateJsonldTemplateReadContextType1', Unset, str]):
        id (Union[Unset, str]):
        type (Union[Unset, str]):
        title (Union[Unset, None, str]): Template title Example: My awesome template!.
        content (Union[Unset, None, str]): The template HTML Example: <html><body><p>My awesome
            template!</p></body</html>.
        thumbnail (Union[Unset, None, str]): The template thumbnail url Example:
            https://assets.easymailing.com/templates/thumbnail.jpg.
        created_at (Union[Unset, None, datetime.datetime]): Date & Time resource created
        updated_at (Union[Unset, None, datetime.datetime]): Date & Time resource updated
        id (Union[Unset, str]):
    """

    context: Union["TemplateJsonldTemplateReadContextType1", Unset, str] = UNSET
    id: Union[Unset, str] = UNSET
    type: Union[Unset, str] = UNSET
    title: Union[Unset, None, str] = UNSET
    content: Union[Unset, None, str] = UNSET
    thumbnail: Union[Unset, None, str] = UNSET
    created_at: Union[Unset, None, datetime.datetime] = UNSET
    updated_at: Union[Unset, None, datetime.datetime] = UNSET
    id: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.template_jsonld_template_read_context_type_1 import TemplateJsonldTemplateReadContextType1

        context: Union[Dict[str, Any], Unset, str]
        if isinstance(self.context, Unset):
            context = UNSET

        elif isinstance(self.context, TemplateJsonldTemplateReadContextType1):
            context = UNSET
            if not isinstance(self.context, Unset):
                context = self.context.to_dict()

        else:
            context = self.context

        id = self.id
        type = self.type
        title = self.title
        content = self.content
        thumbnail = self.thumbnail
        created_at: Union[Unset, None, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat() if self.created_at else None

        updated_at: Union[Unset, None, str] = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat() if self.updated_at else None

        id = self.id

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
        if thumbnail is not UNSET:
            field_dict["thumbnail"] = thumbnail
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at
        if id is not UNSET:
            field_dict["id"] = id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.template_jsonld_template_read_context_type_1 import TemplateJsonldTemplateReadContextType1

        d = src_dict.copy()

        def _parse_context(data: object) -> Union["TemplateJsonldTemplateReadContextType1", Unset, str]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                _context_type_1 = data
                context_type_1: Union[Unset, TemplateJsonldTemplateReadContextType1]
                if isinstance(_context_type_1, Unset):
                    context_type_1 = UNSET
                else:
                    context_type_1 = TemplateJsonldTemplateReadContextType1.from_dict(_context_type_1)

                return context_type_1
            except:  # noqa: E722
                pass
            return cast(Union["TemplateJsonldTemplateReadContextType1", Unset, str], data)

        context = _parse_context(d.pop("@context", UNSET))

        id = d.pop("@id", UNSET)

        type = d.pop("@type", UNSET)

        title = d.pop("title", UNSET)

        content = d.pop("content", UNSET)

        thumbnail = d.pop("thumbnail", UNSET)

        _created_at = d.pop("created_at", UNSET)
        created_at: Union[Unset, None, datetime.datetime]
        if _created_at is None:
            created_at = None
        elif isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        _updated_at = d.pop("updated_at", UNSET)
        updated_at: Union[Unset, None, datetime.datetime]
        if _updated_at is None:
            updated_at = None
        elif isinstance(_updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = isoparse(_updated_at)

        id = d.pop("id", UNSET)

        template_jsonld_template_read = cls(
            context=context,
            id=id,
            type=type,
            title=title,
            content=content,
            thumbnail=thumbnail,
            created_at=created_at,
            updated_at=updated_at,
        )

        template_jsonld_template_read.additional_properties = d
        return template_jsonld_template_read

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
