from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="ListGdprTreatmentPurposeListGdprTreatmentPurposeRead")


@attr.s(auto_attribs=True)
class ListGdprTreatmentPurposeListGdprTreatmentPurposeRead:
    """
    Attributes:
        treatment_purpose (Union[Unset, None, str]):
    """

    treatment_purpose: Union[Unset, None, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        treatment_purpose = self.treatment_purpose

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if treatment_purpose is not UNSET:
            field_dict["treatment_purpose"] = treatment_purpose

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        treatment_purpose = d.pop("treatment_purpose", UNSET)

        list_gdpr_treatment_purpose_list_gdpr_treatment_purpose_read = cls(
            treatment_purpose=treatment_purpose,
        )

        list_gdpr_treatment_purpose_list_gdpr_treatment_purpose_read.additional_properties = d
        return list_gdpr_treatment_purpose_list_gdpr_treatment_purpose_read

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
