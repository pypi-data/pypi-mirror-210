import datetime
from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="ConsentContactWrite")


@attr.s(auto_attribs=True)
class ConsentContactWrite:
    """
    Attributes:
        ip (str): Ip address to confirm opt-in Example: 10.0.0.1.
        consent_at (datetime.datetime): Consent date Example: 2020-01-01T00:00:00+00:00.
        list_gdpr_treatment_purposes (Union[Unset, List[str]]): Audience treatment purposes accepted by the contact
    """

    ip: str
    consent_at: datetime.datetime
    list_gdpr_treatment_purposes: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        ip = self.ip
        consent_at = self.consent_at.isoformat()

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
        if list_gdpr_treatment_purposes is not UNSET:
            field_dict["list_gdpr_treatment_purposes"] = list_gdpr_treatment_purposes

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        ip = d.pop("ip")

        consent_at = isoparse(d.pop("consent_at"))

        list_gdpr_treatment_purposes = cast(List[str], d.pop("list_gdpr_treatment_purposes", UNSET))

        consent_contact_write = cls(
            ip=ip,
            consent_at=consent_at,
            list_gdpr_treatment_purposes=list_gdpr_treatment_purposes,
        )

        consent_contact_write.additional_properties = d
        return consent_contact_write

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
