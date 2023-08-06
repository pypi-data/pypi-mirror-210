from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="LocationContactRead")


@attr.s(auto_attribs=True)
class LocationContactRead:
    """
    Attributes:
        city (Union[Unset, str]): City Example: Madrid.
        postal_code (Union[Unset, str]): Postal code Example: 28001.
        timezone (Union[Unset, str]): Timezone Example: Europe/Madrid.
        lat (Union[Unset, float]): Latitude Example: 40.416775.
        lng (Union[Unset, float]): Longitude Example: -3.70379.
        country_code (Union[Unset, str]): Country code Example: ES.
        country (Union[Unset, str]): Country Example: Spain.
    """

    city: Union[Unset, str] = UNSET
    postal_code: Union[Unset, str] = UNSET
    timezone: Union[Unset, str] = UNSET
    lat: Union[Unset, float] = UNSET
    lng: Union[Unset, float] = UNSET
    country_code: Union[Unset, str] = UNSET
    country: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        city = self.city
        postal_code = self.postal_code
        timezone = self.timezone
        lat = self.lat
        lng = self.lng
        country_code = self.country_code
        country = self.country

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if city is not UNSET:
            field_dict["city"] = city
        if postal_code is not UNSET:
            field_dict["postal_code"] = postal_code
        if timezone is not UNSET:
            field_dict["timezone"] = timezone
        if lat is not UNSET:
            field_dict["lat"] = lat
        if lng is not UNSET:
            field_dict["lng"] = lng
        if country_code is not UNSET:
            field_dict["country_code"] = country_code
        if country is not UNSET:
            field_dict["country"] = country

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        city = d.pop("city", UNSET)

        postal_code = d.pop("postal_code", UNSET)

        timezone = d.pop("timezone", UNSET)

        lat = d.pop("lat", UNSET)

        lng = d.pop("lng", UNSET)

        country_code = d.pop("country_code", UNSET)

        country = d.pop("country", UNSET)

        location_contact_read = cls(
            city=city,
            postal_code=postal_code,
            timezone=timezone,
            lat=lat,
            lng=lng,
            country_code=country_code,
            country=country,
        )

        location_contact_read.additional_properties = d
        return location_contact_read

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
