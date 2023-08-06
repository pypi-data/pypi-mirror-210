from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.consent_jsonld_suscriber_consent_read_context_type_1 import (
        ConsentJsonldSuscriberConsentReadContextType1,
    )


T = TypeVar("T", bound="ConsentJsonldSuscriberConsentRead")


@attr.s(auto_attribs=True)
class ConsentJsonldSuscriberConsentRead:
    """
    Attributes:
        id (Union[Unset, str]):
        type (Union[Unset, str]):
        context (Union['ConsentJsonldSuscriberConsentReadContextType1', Unset, str]):
    """

    id: Union[Unset, str] = UNSET
    type: Union[Unset, str] = UNSET
    context: Union["ConsentJsonldSuscriberConsentReadContextType1", Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.consent_jsonld_suscriber_consent_read_context_type_1 import (
            ConsentJsonldSuscriberConsentReadContextType1,
        )

        id = self.id
        type = self.type
        context: Union[Dict[str, Any], Unset, str]
        if isinstance(self.context, Unset):
            context = UNSET

        elif isinstance(self.context, ConsentJsonldSuscriberConsentReadContextType1):
            context = UNSET
            if not isinstance(self.context, Unset):
                context = self.context.to_dict()

        else:
            context = self.context

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["@id"] = id
        if type is not UNSET:
            field_dict["@type"] = type
        if context is not UNSET:
            field_dict["@context"] = context

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.consent_jsonld_suscriber_consent_read_context_type_1 import (
            ConsentJsonldSuscriberConsentReadContextType1,
        )

        d = src_dict.copy()
        id = d.pop("@id", UNSET)

        type = d.pop("@type", UNSET)

        def _parse_context(data: object) -> Union["ConsentJsonldSuscriberConsentReadContextType1", Unset, str]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                _context_type_1 = data
                context_type_1: Union[Unset, ConsentJsonldSuscriberConsentReadContextType1]
                if isinstance(_context_type_1, Unset):
                    context_type_1 = UNSET
                else:
                    context_type_1 = ConsentJsonldSuscriberConsentReadContextType1.from_dict(_context_type_1)

                return context_type_1
            except:  # noqa: E722
                pass
            return cast(Union["ConsentJsonldSuscriberConsentReadContextType1", Unset, str], data)

        context = _parse_context(d.pop("@context", UNSET))

        consent_jsonld_suscriber_consent_read = cls(
            id=id,
            type=type,
            context=context,
        )

        consent_jsonld_suscriber_consent_read.additional_properties = d
        return consent_jsonld_suscriber_consent_read

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
