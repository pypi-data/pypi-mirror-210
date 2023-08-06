from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.sender_jsonld_sender_write_context_type_1 import SenderJsonldSenderWriteContextType1


T = TypeVar("T", bound="SenderJsonldSenderWrite")


@attr.s(auto_attribs=True)
class SenderJsonldSenderWrite:
    """
    Attributes:
        context (Union['SenderJsonldSenderWriteContextType1', Unset, str]):
        id (Union[Unset, str]):
        type (Union[Unset, str]):
        email (Union[Unset, None, str]): The email to confirm Example: user@company.com.
    """

    context: Union["SenderJsonldSenderWriteContextType1", Unset, str] = UNSET
    id: Union[Unset, str] = UNSET
    type: Union[Unset, str] = UNSET
    email: Union[Unset, None, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.sender_jsonld_sender_write_context_type_1 import SenderJsonldSenderWriteContextType1

        context: Union[Dict[str, Any], Unset, str]
        if isinstance(self.context, Unset):
            context = UNSET

        elif isinstance(self.context, SenderJsonldSenderWriteContextType1):
            context = UNSET
            if not isinstance(self.context, Unset):
                context = self.context.to_dict()

        else:
            context = self.context

        id = self.id
        type = self.type
        email = self.email

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if context is not UNSET:
            field_dict["@context"] = context
        if id is not UNSET:
            field_dict["@id"] = id
        if type is not UNSET:
            field_dict["@type"] = type
        if email is not UNSET:
            field_dict["email"] = email

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.sender_jsonld_sender_write_context_type_1 import SenderJsonldSenderWriteContextType1

        d = src_dict.copy()

        def _parse_context(data: object) -> Union["SenderJsonldSenderWriteContextType1", Unset, str]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                _context_type_1 = data
                context_type_1: Union[Unset, SenderJsonldSenderWriteContextType1]
                if isinstance(_context_type_1, Unset):
                    context_type_1 = UNSET
                else:
                    context_type_1 = SenderJsonldSenderWriteContextType1.from_dict(_context_type_1)

                return context_type_1
            except:  # noqa: E722
                pass
            return cast(Union["SenderJsonldSenderWriteContextType1", Unset, str], data)

        context = _parse_context(d.pop("@context", UNSET))

        id = d.pop("@id", UNSET)

        type = d.pop("@type", UNSET)

        email = d.pop("email", UNSET)

        sender_jsonld_sender_write = cls(
            context=context,
            id=id,
            type=type,
            email=email,
        )

        sender_jsonld_sender_write.additional_properties = d
        return sender_jsonld_sender_write

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
