import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

import attr
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.consent_jsonld_contact_write_context_type_1 import ConsentJsonldContactWriteContextType1


T = TypeVar("T", bound="ConsentJsonldContactWrite")


@attr.s(auto_attribs=True)
class ConsentJsonldContactWrite:
    """
    Attributes:
        ip (str): Ip address to confirm opt-in Example: 10.0.0.1.
        consent_at (datetime.datetime): Consent date Example: 2020-01-01T00:00:00+00:00.
        context (Union['ConsentJsonldContactWriteContextType1', Unset, str]):
        id (Union[Unset, str]):
        type (Union[Unset, str]):
        list_gdpr_treatment_purposes (Union[Unset, List[str]]): Audience treatment purposes accepted by the contact
    """

    ip: str
    consent_at: datetime.datetime
    context: Union["ConsentJsonldContactWriteContextType1", Unset, str] = UNSET
    id: Union[Unset, str] = UNSET
    type: Union[Unset, str] = UNSET
    list_gdpr_treatment_purposes: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.consent_jsonld_contact_write_context_type_1 import ConsentJsonldContactWriteContextType1

        ip = self.ip
        consent_at = self.consent_at.isoformat()

        context: Union[Dict[str, Any], Unset, str]
        if isinstance(self.context, Unset):
            context = UNSET

        elif isinstance(self.context, ConsentJsonldContactWriteContextType1):
            context = UNSET
            if not isinstance(self.context, Unset):
                context = self.context.to_dict()

        else:
            context = self.context

        id = self.id
        type = self.type
        list_gdpr_treatment_purposes: Union[Unset, List[str]] = UNSET
        if not isinstance(self.list_gdpr_treatment_purposes, Unset):
            list_gdpr_treatment_purposes = self.list_gdpr_treatment_purposes

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ip": ip,
                "consent_at": consent_at,
            }
        )
        if context is not UNSET:
            field_dict["@context"] = context
        if id is not UNSET:
            field_dict["@id"] = id
        if type is not UNSET:
            field_dict["@type"] = type
        if list_gdpr_treatment_purposes is not UNSET:
            field_dict["list_gdpr_treatment_purposes"] = list_gdpr_treatment_purposes

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.consent_jsonld_contact_write_context_type_1 import ConsentJsonldContactWriteContextType1

        d = src_dict.copy()
        ip = d.pop("ip")

        consent_at = isoparse(d.pop("consent_at"))

        def _parse_context(data: object) -> Union["ConsentJsonldContactWriteContextType1", Unset, str]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                _context_type_1 = data
                context_type_1: Union[Unset, ConsentJsonldContactWriteContextType1]
                if isinstance(_context_type_1, Unset):
                    context_type_1 = UNSET
                else:
                    context_type_1 = ConsentJsonldContactWriteContextType1.from_dict(_context_type_1)

                return context_type_1
            except:  # noqa: E722
                pass
            return cast(Union["ConsentJsonldContactWriteContextType1", Unset, str], data)

        context = _parse_context(d.pop("@context", UNSET))

        id = d.pop("@id", UNSET)

        type = d.pop("@type", UNSET)

        list_gdpr_treatment_purposes = cast(List[str], d.pop("list_gdpr_treatment_purposes", UNSET))

        consent_jsonld_contact_write = cls(
            ip=ip,
            consent_at=consent_at,
            context=context,
            id=id,
            type=type,
            list_gdpr_treatment_purposes=list_gdpr_treatment_purposes,
        )

        consent_jsonld_contact_write.additional_properties = d
        return consent_jsonld_contact_write

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
