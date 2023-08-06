from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.list_gdpr_treatment_purpose_jsonld_audience_read_context_type_1 import (
        ListGdprTreatmentPurposeJsonldAudienceReadContextType1,
    )
    from ..models.treatment_purpose_jsonld_audience_read import TreatmentPurposeJsonldAudienceRead


T = TypeVar("T", bound="ListGdprTreatmentPurposeJsonldAudienceRead")


@attr.s(auto_attribs=True)
class ListGdprTreatmentPurposeJsonldAudienceRead:
    """
    Attributes:
        context (Union['ListGdprTreatmentPurposeJsonldAudienceReadContextType1', Unset, str]):
        id (Union[Unset, str]):
        type (Union[Unset, str]):
        treatment_purpose (Union[Unset, None, TreatmentPurposeJsonldAudienceRead]):
    """

    context: Union["ListGdprTreatmentPurposeJsonldAudienceReadContextType1", Unset, str] = UNSET
    id: Union[Unset, str] = UNSET
    type: Union[Unset, str] = UNSET
    treatment_purpose: Union[Unset, None, "TreatmentPurposeJsonldAudienceRead"] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.list_gdpr_treatment_purpose_jsonld_audience_read_context_type_1 import (
            ListGdprTreatmentPurposeJsonldAudienceReadContextType1,
        )

        context: Union[Dict[str, Any], Unset, str]
        if isinstance(self.context, Unset):
            context = UNSET

        elif isinstance(self.context, ListGdprTreatmentPurposeJsonldAudienceReadContextType1):
            context = UNSET
            if not isinstance(self.context, Unset):
                context = self.context.to_dict()

        else:
            context = self.context

        id = self.id
        type = self.type
        treatment_purpose: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.treatment_purpose, Unset):
            treatment_purpose = self.treatment_purpose.to_dict() if self.treatment_purpose else None

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if context is not UNSET:
            field_dict["@context"] = context
        if id is not UNSET:
            field_dict["@id"] = id
        if type is not UNSET:
            field_dict["@type"] = type
        if treatment_purpose is not UNSET:
            field_dict["treatment_purpose"] = treatment_purpose

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.list_gdpr_treatment_purpose_jsonld_audience_read_context_type_1 import (
            ListGdprTreatmentPurposeJsonldAudienceReadContextType1,
        )
        from ..models.treatment_purpose_jsonld_audience_read import TreatmentPurposeJsonldAudienceRead

        d = src_dict.copy()

        def _parse_context(data: object) -> Union["ListGdprTreatmentPurposeJsonldAudienceReadContextType1", Unset, str]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                _context_type_1 = data
                context_type_1: Union[Unset, ListGdprTreatmentPurposeJsonldAudienceReadContextType1]
                if isinstance(_context_type_1, Unset):
                    context_type_1 = UNSET
                else:
                    context_type_1 = ListGdprTreatmentPurposeJsonldAudienceReadContextType1.from_dict(_context_type_1)

                return context_type_1
            except:  # noqa: E722
                pass
            return cast(Union["ListGdprTreatmentPurposeJsonldAudienceReadContextType1", Unset, str], data)

        context = _parse_context(d.pop("@context", UNSET))

        id = d.pop("@id", UNSET)

        type = d.pop("@type", UNSET)

        _treatment_purpose = d.pop("treatment_purpose", UNSET)
        treatment_purpose: Union[Unset, None, TreatmentPurposeJsonldAudienceRead]
        if _treatment_purpose is None:
            treatment_purpose = None
        elif isinstance(_treatment_purpose, Unset):
            treatment_purpose = UNSET
        else:
            treatment_purpose = TreatmentPurposeJsonldAudienceRead.from_dict(_treatment_purpose)

        list_gdpr_treatment_purpose_jsonld_audience_read = cls(
            context=context,
            id=id,
            type=type,
            treatment_purpose=treatment_purpose,
        )

        list_gdpr_treatment_purpose_jsonld_audience_read.additional_properties = d
        return list_gdpr_treatment_purpose_jsonld_audience_read

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
