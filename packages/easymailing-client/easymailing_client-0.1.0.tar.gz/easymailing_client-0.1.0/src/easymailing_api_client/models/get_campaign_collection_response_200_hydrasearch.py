from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_campaign_collection_response_200_hydrasearch_hydramapping_item import (
        GetCampaignCollectionResponse200HydrasearchHydramappingItem,
    )


T = TypeVar("T", bound="GetCampaignCollectionResponse200Hydrasearch")


@attr.s(auto_attribs=True)
class GetCampaignCollectionResponse200Hydrasearch:
    """
    Attributes:
        type (Union[Unset, str]):
        hydratemplate (Union[Unset, str]):
        hydravariable_representation (Union[Unset, str]):
        hydramapping (Union[Unset, List['GetCampaignCollectionResponse200HydrasearchHydramappingItem']]):
    """

    type: Union[Unset, str] = UNSET
    hydratemplate: Union[Unset, str] = UNSET
    hydravariable_representation: Union[Unset, str] = UNSET
    hydramapping: Union[Unset, List["GetCampaignCollectionResponse200HydrasearchHydramappingItem"]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        type = self.type
        hydratemplate = self.hydratemplate
        hydravariable_representation = self.hydravariable_representation
        hydramapping: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.hydramapping, Unset):
            hydramapping = []
            for hydramapping_item_data in self.hydramapping:
                hydramapping_item = hydramapping_item_data.to_dict()

                hydramapping.append(hydramapping_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if type is not UNSET:
            field_dict["@type"] = type
        if hydratemplate is not UNSET:
            field_dict["hydra:template"] = hydratemplate
        if hydravariable_representation is not UNSET:
            field_dict["hydra:variableRepresentation"] = hydravariable_representation
        if hydramapping is not UNSET:
            field_dict["hydra:mapping"] = hydramapping

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.get_campaign_collection_response_200_hydrasearch_hydramapping_item import (
            GetCampaignCollectionResponse200HydrasearchHydramappingItem,
        )

        d = src_dict.copy()
        type = d.pop("@type", UNSET)

        hydratemplate = d.pop("hydra:template", UNSET)

        hydravariable_representation = d.pop("hydra:variableRepresentation", UNSET)

        hydramapping = []
        _hydramapping = d.pop("hydra:mapping", UNSET)
        for hydramapping_item_data in _hydramapping or []:
            hydramapping_item = GetCampaignCollectionResponse200HydrasearchHydramappingItem.from_dict(
                hydramapping_item_data
            )

            hydramapping.append(hydramapping_item)

        get_campaign_collection_response_200_hydrasearch = cls(
            type=type,
            hydratemplate=hydratemplate,
            hydravariable_representation=hydravariable_representation,
            hydramapping=hydramapping,
        )

        get_campaign_collection_response_200_hydrasearch.additional_properties = d
        return get_campaign_collection_response_200_hydrasearch

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
