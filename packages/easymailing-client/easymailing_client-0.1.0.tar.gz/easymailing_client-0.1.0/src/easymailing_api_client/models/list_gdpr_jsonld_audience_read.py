from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.data_manager_jsonld_audience_read import DataManagerJsonldAudienceRead
    from ..models.list_gdpr_jsonld_audience_read_context_type_1 import ListGdprJsonldAudienceReadContextType1
    from ..models.list_gdpr_treatment_purpose_jsonld_audience_read import ListGdprTreatmentPurposeJsonldAudienceRead


T = TypeVar("T", bound="ListGdprJsonldAudienceRead")


@attr.s(auto_attribs=True)
class ListGdprJsonldAudienceRead:
    """
    Attributes:
        context (Union['ListGdprJsonldAudienceReadContextType1', Unset, str]):
        id (Union[Unset, str]):
        type (Union[Unset, str]):
        enabled (Union[Unset, None, str]): Enable GDPR tools
        privacy_url (Union[Unset, None, str]):
        list_gdpr_treatment_purposes (Union[Unset, List['ListGdprTreatmentPurposeJsonldAudienceRead']]):
        data_manager (Union[Unset, None, DataManagerJsonldAudienceRead]):
    """

    context: Union["ListGdprJsonldAudienceReadContextType1", Unset, str] = UNSET
    id: Union[Unset, str] = UNSET
    type: Union[Unset, str] = UNSET
    enabled: Union[Unset, None, str] = UNSET
    privacy_url: Union[Unset, None, str] = UNSET
    list_gdpr_treatment_purposes: Union[Unset, List["ListGdprTreatmentPurposeJsonldAudienceRead"]] = UNSET
    data_manager: Union[Unset, None, "DataManagerJsonldAudienceRead"] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.list_gdpr_jsonld_audience_read_context_type_1 import ListGdprJsonldAudienceReadContextType1

        context: Union[Dict[str, Any], Unset, str]
        if isinstance(self.context, Unset):
            context = UNSET

        elif isinstance(self.context, ListGdprJsonldAudienceReadContextType1):
            context = UNSET
            if not isinstance(self.context, Unset):
                context = self.context.to_dict()

        else:
            context = self.context

        id = self.id
        type = self.type
        enabled = self.enabled
        privacy_url = self.privacy_url
        list_gdpr_treatment_purposes: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.list_gdpr_treatment_purposes, Unset):
            list_gdpr_treatment_purposes = []
            for list_gdpr_treatment_purposes_item_data in self.list_gdpr_treatment_purposes:
                list_gdpr_treatment_purposes_item = list_gdpr_treatment_purposes_item_data.to_dict()

                list_gdpr_treatment_purposes.append(list_gdpr_treatment_purposes_item)

        data_manager: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.data_manager, Unset):
            data_manager = self.data_manager.to_dict() if self.data_manager else None

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if context is not UNSET:
            field_dict["@context"] = context
        if id is not UNSET:
            field_dict["@id"] = id
        if type is not UNSET:
            field_dict["@type"] = type
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if privacy_url is not UNSET:
            field_dict["privacy_url"] = privacy_url
        if list_gdpr_treatment_purposes is not UNSET:
            field_dict["list_gdpr_treatment_purposes"] = list_gdpr_treatment_purposes
        if data_manager is not UNSET:
            field_dict["data_manager"] = data_manager

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.data_manager_jsonld_audience_read import DataManagerJsonldAudienceRead
        from ..models.list_gdpr_jsonld_audience_read_context_type_1 import ListGdprJsonldAudienceReadContextType1
        from ..models.list_gdpr_treatment_purpose_jsonld_audience_read import ListGdprTreatmentPurposeJsonldAudienceRead

        d = src_dict.copy()

        def _parse_context(data: object) -> Union["ListGdprJsonldAudienceReadContextType1", Unset, str]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                _context_type_1 = data
                context_type_1: Union[Unset, ListGdprJsonldAudienceReadContextType1]
                if isinstance(_context_type_1, Unset):
                    context_type_1 = UNSET
                else:
                    context_type_1 = ListGdprJsonldAudienceReadContextType1.from_dict(_context_type_1)

                return context_type_1
            except:  # noqa: E722
                pass
            return cast(Union["ListGdprJsonldAudienceReadContextType1", Unset, str], data)

        context = _parse_context(d.pop("@context", UNSET))

        id = d.pop("@id", UNSET)

        type = d.pop("@type", UNSET)

        enabled = d.pop("enabled", UNSET)

        privacy_url = d.pop("privacy_url", UNSET)

        list_gdpr_treatment_purposes = []
        _list_gdpr_treatment_purposes = d.pop("list_gdpr_treatment_purposes", UNSET)
        for list_gdpr_treatment_purposes_item_data in _list_gdpr_treatment_purposes or []:
            list_gdpr_treatment_purposes_item = ListGdprTreatmentPurposeJsonldAudienceRead.from_dict(
                list_gdpr_treatment_purposes_item_data
            )

            list_gdpr_treatment_purposes.append(list_gdpr_treatment_purposes_item)

        _data_manager = d.pop("data_manager", UNSET)
        data_manager: Union[Unset, None, DataManagerJsonldAudienceRead]
        if _data_manager is None:
            data_manager = None
        elif isinstance(_data_manager, Unset):
            data_manager = UNSET
        else:
            data_manager = DataManagerJsonldAudienceRead.from_dict(_data_manager)

        list_gdpr_jsonld_audience_read = cls(
            context=context,
            id=id,
            type=type,
            enabled=enabled,
            privacy_url=privacy_url,
            list_gdpr_treatment_purposes=list_gdpr_treatment_purposes,
            data_manager=data_manager,
        )

        list_gdpr_jsonld_audience_read.additional_properties = d
        return list_gdpr_jsonld_audience_read

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
