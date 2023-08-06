from typing import Any, Dict, List, Type, TypeVar

import attr

from ..models.list_gdpr_treatment_purpose_jsonld_contact_read_context_type_1_hydra import (
    ListGdprTreatmentPurposeJsonldContactReadContextType1Hydra,
)

T = TypeVar("T", bound="ListGdprTreatmentPurposeJsonldContactReadContextType1")


@attr.s(auto_attribs=True)
class ListGdprTreatmentPurposeJsonldContactReadContextType1:
    """
    Attributes:
        vocab (str):
        hydra (ListGdprTreatmentPurposeJsonldContactReadContextType1Hydra):
    """

    vocab: str
    hydra: ListGdprTreatmentPurposeJsonldContactReadContextType1Hydra
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        vocab = self.vocab
        hydra = self.hydra.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "@vocab": vocab,
                "hydra": hydra,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        vocab = d.pop("@vocab")

        hydra = ListGdprTreatmentPurposeJsonldContactReadContextType1Hydra(d.pop("hydra"))

        list_gdpr_treatment_purpose_jsonld_contact_read_context_type_1 = cls(
            vocab=vocab,
            hydra=hydra,
        )

        list_gdpr_treatment_purpose_jsonld_contact_read_context_type_1.additional_properties = d
        return list_gdpr_treatment_purpose_jsonld_contact_read_context_type_1

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
