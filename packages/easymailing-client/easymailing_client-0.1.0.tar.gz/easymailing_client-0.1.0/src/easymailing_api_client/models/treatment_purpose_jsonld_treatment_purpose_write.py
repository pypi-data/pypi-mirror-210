from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.treatment_purpose_jsonld_treatment_purpose_write_context_type_1 import (
        TreatmentPurposeJsonldTreatmentPurposeWriteContextType1,
    )


T = TypeVar("T", bound="TreatmentPurposeJsonldTreatmentPurposeWrite")


@attr.s(auto_attribs=True)
class TreatmentPurposeJsonldTreatmentPurposeWrite:
    """
    Attributes:
        context (Union['TreatmentPurposeJsonldTreatmentPurposeWriteContextType1', Unset, str]):
        id (Union[Unset, str]):
        type (Union[Unset, str]):
        name (Union[Unset, None, str]): Name Example: I accept the sending of commercial communications and / or
            Newsletters.
        description (Union[Unset, None, str]): Description Example: Commercial newsletters.
        custom (Union[Unset, None, bool]): Is custom treatment purpose
    """

    context: Union["TreatmentPurposeJsonldTreatmentPurposeWriteContextType1", Unset, str] = UNSET
    id: Union[Unset, str] = UNSET
    type: Union[Unset, str] = UNSET
    name: Union[Unset, None, str] = UNSET
    description: Union[Unset, None, str] = UNSET
    custom: Union[Unset, None, bool] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.treatment_purpose_jsonld_treatment_purpose_write_context_type_1 import (
            TreatmentPurposeJsonldTreatmentPurposeWriteContextType1,
        )

        context: Union[Dict[str, Any], Unset, str]
        if isinstance(self.context, Unset):
            context = UNSET

        elif isinstance(self.context, TreatmentPurposeJsonldTreatmentPurposeWriteContextType1):
            context = UNSET
            if not isinstance(self.context, Unset):
                context = self.context.to_dict()

        else:
            context = self.context

        id = self.id
        type = self.type
        name = self.name
        description = self.description
        custom = self.custom

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if context is not UNSET:
            field_dict["@context"] = context
        if id is not UNSET:
            field_dict["@id"] = id
        if type is not UNSET:
            field_dict["@type"] = type
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if custom is not UNSET:
            field_dict["custom"] = custom

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.treatment_purpose_jsonld_treatment_purpose_write_context_type_1 import (
            TreatmentPurposeJsonldTreatmentPurposeWriteContextType1,
        )

        d = src_dict.copy()

        def _parse_context(
            data: object,
        ) -> Union["TreatmentPurposeJsonldTreatmentPurposeWriteContextType1", Unset, str]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                _context_type_1 = data
                context_type_1: Union[Unset, TreatmentPurposeJsonldTreatmentPurposeWriteContextType1]
                if isinstance(_context_type_1, Unset):
                    context_type_1 = UNSET
                else:
                    context_type_1 = TreatmentPurposeJsonldTreatmentPurposeWriteContextType1.from_dict(_context_type_1)

                return context_type_1
            except:  # noqa: E722
                pass
            return cast(Union["TreatmentPurposeJsonldTreatmentPurposeWriteContextType1", Unset, str], data)

        context = _parse_context(d.pop("@context", UNSET))

        id = d.pop("@id", UNSET)

        type = d.pop("@type", UNSET)

        name = d.pop("name", UNSET)

        description = d.pop("description", UNSET)

        custom = d.pop("custom", UNSET)

        treatment_purpose_jsonld_treatment_purpose_write = cls(
            context=context,
            id=id,
            type=type,
            name=name,
            description=description,
            custom=custom,
        )

        treatment_purpose_jsonld_treatment_purpose_write.additional_properties = d
        return treatment_purpose_jsonld_treatment_purpose_write

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
