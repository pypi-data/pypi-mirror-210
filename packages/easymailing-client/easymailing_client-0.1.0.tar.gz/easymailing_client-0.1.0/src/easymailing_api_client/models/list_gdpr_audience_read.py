from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.data_manager_audience_read import DataManagerAudienceRead
    from ..models.list_gdpr_treatment_purpose_audience_read import ListGdprTreatmentPurposeAudienceRead


T = TypeVar("T", bound="ListGdprAudienceRead")


@attr.s(auto_attribs=True)
class ListGdprAudienceRead:
    """
    Attributes:
        enabled (Union[Unset, None, str]): Enable GDPR tools
        privacy_url (Union[Unset, None, str]):
        list_gdpr_treatment_purposes (Union[Unset, List['ListGdprTreatmentPurposeAudienceRead']]):
        data_manager (Union[Unset, None, DataManagerAudienceRead]):
    """

    enabled: Union[Unset, None, str] = UNSET
    privacy_url: Union[Unset, None, str] = UNSET
    list_gdpr_treatment_purposes: Union[Unset, List["ListGdprTreatmentPurposeAudienceRead"]] = UNSET
    data_manager: Union[Unset, None, "DataManagerAudienceRead"] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
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
        from ..models.data_manager_audience_read import DataManagerAudienceRead
        from ..models.list_gdpr_treatment_purpose_audience_read import ListGdprTreatmentPurposeAudienceRead

        d = src_dict.copy()
        enabled = d.pop("enabled", UNSET)

        privacy_url = d.pop("privacy_url", UNSET)

        list_gdpr_treatment_purposes = []
        _list_gdpr_treatment_purposes = d.pop("list_gdpr_treatment_purposes", UNSET)
        for list_gdpr_treatment_purposes_item_data in _list_gdpr_treatment_purposes or []:
            list_gdpr_treatment_purposes_item = ListGdprTreatmentPurposeAudienceRead.from_dict(
                list_gdpr_treatment_purposes_item_data
            )

            list_gdpr_treatment_purposes.append(list_gdpr_treatment_purposes_item)

        _data_manager = d.pop("data_manager", UNSET)
        data_manager: Union[Unset, None, DataManagerAudienceRead]
        if _data_manager is None:
            data_manager = None
        elif isinstance(_data_manager, Unset):
            data_manager = UNSET
        else:
            data_manager = DataManagerAudienceRead.from_dict(_data_manager)

        list_gdpr_audience_read = cls(
            enabled=enabled,
            privacy_url=privacy_url,
            list_gdpr_treatment_purposes=list_gdpr_treatment_purposes,
            data_manager=data_manager,
        )

        list_gdpr_audience_read.additional_properties = d
        return list_gdpr_audience_read

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
