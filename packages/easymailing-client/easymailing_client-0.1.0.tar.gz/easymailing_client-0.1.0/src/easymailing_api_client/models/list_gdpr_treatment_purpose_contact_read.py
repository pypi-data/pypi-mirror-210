from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.treatment_purpose_contact_read import TreatmentPurposeContactRead


T = TypeVar("T", bound="ListGdprTreatmentPurposeContactRead")


@attr.s(auto_attribs=True)
class ListGdprTreatmentPurposeContactRead:
    """
    Attributes:
        treatment_purpose (Union[Unset, None, TreatmentPurposeContactRead]):
    """

    treatment_purpose: Union[Unset, None, "TreatmentPurposeContactRead"] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        treatment_purpose: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.treatment_purpose, Unset):
            treatment_purpose = self.treatment_purpose.to_dict() if self.treatment_purpose else None

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if treatment_purpose is not UNSET:
            field_dict["treatment_purpose"] = treatment_purpose

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.treatment_purpose_contact_read import TreatmentPurposeContactRead

        d = src_dict.copy()
        _treatment_purpose = d.pop("treatment_purpose", UNSET)
        treatment_purpose: Union[Unset, None, TreatmentPurposeContactRead]
        if _treatment_purpose is None:
            treatment_purpose = None
        elif isinstance(_treatment_purpose, Unset):
            treatment_purpose = UNSET
        else:
            treatment_purpose = TreatmentPurposeContactRead.from_dict(_treatment_purpose)

        list_gdpr_treatment_purpose_contact_read = cls(
            treatment_purpose=treatment_purpose,
        )

        list_gdpr_treatment_purpose_contact_read.additional_properties = d
        return list_gdpr_treatment_purpose_contact_read

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
