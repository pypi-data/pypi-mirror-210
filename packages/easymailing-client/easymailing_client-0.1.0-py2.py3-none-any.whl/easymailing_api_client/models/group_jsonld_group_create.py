from typing import TYPE_CHECKING, Any, Dict, List, Optional, Type, TypeVar, Union, cast

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.group_jsonld_group_create_context_type_1 import GroupJsonldGroupCreateContextType1


T = TypeVar("T", bound="GroupJsonldGroupCreate")


@attr.s(auto_attribs=True)
class GroupJsonldGroupCreate:
    """
    Attributes:
        context (Union['GroupJsonldGroupCreateContextType1', Unset, str]):
        id (Union[Unset, str]):
        type (Union[Unset, str]):
        title (Optional[str]): Group title Example: My newsletter group.
        description (Union[Unset, None, str]): Group description Example: Newsletter suscribers.
        color (Union[Unset, None, str]): Group color Example: #263238.
        public (Union[Unset, None, bool]): Is public? Example: True.
        audience (Optional[str]): Audience Example: /audiences/0df14405-90ff-4287-b3e4-ef088901ee6f.
    """

    title: Optional[str]
    audience: Optional[str]
    context: Union["GroupJsonldGroupCreateContextType1", Unset, str] = UNSET
    id: Union[Unset, str] = UNSET
    type: Union[Unset, str] = UNSET
    description: Union[Unset, None, str] = UNSET
    color: Union[Unset, None, str] = UNSET
    public: Union[Unset, None, bool] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.group_jsonld_group_create_context_type_1 import GroupJsonldGroupCreateContextType1

        context: Union[Dict[str, Any], Unset, str]
        if isinstance(self.context, Unset):
            context = UNSET

        elif isinstance(self.context, GroupJsonldGroupCreateContextType1):
            context = UNSET
            if not isinstance(self.context, Unset):
                context = self.context.to_dict()

        else:
            context = self.context

        id = self.id
        type = self.type
        title = self.title
        description = self.description
        color = self.color
        public = self.public
        audience = self.audience

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "title": title,
                "audience": audience,
            }
        )
        if context is not UNSET:
            field_dict["@context"] = context
        if id is not UNSET:
            field_dict["@id"] = id
        if type is not UNSET:
            field_dict["@type"] = type
        if description is not UNSET:
            field_dict["description"] = description
        if color is not UNSET:
            field_dict["color"] = color
        if public is not UNSET:
            field_dict["public"] = public

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.group_jsonld_group_create_context_type_1 import GroupJsonldGroupCreateContextType1

        d = src_dict.copy()

        def _parse_context(data: object) -> Union["GroupJsonldGroupCreateContextType1", Unset, str]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                _context_type_1 = data
                context_type_1: Union[Unset, GroupJsonldGroupCreateContextType1]
                if isinstance(_context_type_1, Unset):
                    context_type_1 = UNSET
                else:
                    context_type_1 = GroupJsonldGroupCreateContextType1.from_dict(_context_type_1)

                return context_type_1
            except:  # noqa: E722
                pass
            return cast(Union["GroupJsonldGroupCreateContextType1", Unset, str], data)

        context = _parse_context(d.pop("@context", UNSET))

        id = d.pop("@id", UNSET)

        type = d.pop("@type", UNSET)

        title = d.pop("title")

        description = d.pop("description", UNSET)

        color = d.pop("color", UNSET)

        public = d.pop("public", UNSET)

        audience = d.pop("audience")

        group_jsonld_group_create = cls(
            context=context,
            id=id,
            type=type,
            title=title,
            description=description,
            color=color,
            public=public,
            audience=audience,
        )

        group_jsonld_group_create.additional_properties = d
        return group_jsonld_group_create

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
