from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.location_jsonld_contact_read_context_type_1 import LocationJsonldContactReadContextType1


T = TypeVar("T", bound="LocationJsonldContactRead")


@attr.s(auto_attribs=True)
class LocationJsonldContactRead:
    """
    Attributes:
        context (Union['LocationJsonldContactReadContextType1', Unset, str]):
        id (Union[Unset, str]):
        type (Union[Unset, str]):
        city (Union[Unset, str]): City Example: Madrid.
        postal_code (Union[Unset, str]): Postal code Example: 28001.
        timezone (Union[Unset, str]): Timezone Example: Europe/Madrid.
        lat (Union[Unset, float]): Latitude Example: 40.416775.
        lng (Union[Unset, float]): Longitude Example: -3.70379.
        country_code (Union[Unset, str]): Country code Example: ES.
        country (Union[Unset, str]): Country Example: Spain.
    """

    context: Union["LocationJsonldContactReadContextType1", Unset, str] = UNSET
    id: Union[Unset, str] = UNSET
    type: Union[Unset, str] = UNSET
    city: Union[Unset, str] = UNSET
    postal_code: Union[Unset, str] = UNSET
    timezone: Union[Unset, str] = UNSET
    lat: Union[Unset, float] = UNSET
    lng: Union[Unset, float] = UNSET
    country_code: Union[Unset, str] = UNSET
    country: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.location_jsonld_contact_read_context_type_1 import LocationJsonldContactReadContextType1

        context: Union[Dict[str, Any], Unset, str]
        if isinstance(self.context, Unset):
            context = UNSET

        elif isinstance(self.context, LocationJsonldContactReadContextType1):
            context = UNSET
            if not isinstance(self.context, Unset):
                context = self.context.to_dict()

        else:
            context = self.context

        id = self.id
        type = self.type
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
        if context is not UNSET:
            field_dict["@context"] = context
        if id is not UNSET:
            field_dict["@id"] = id
        if type is not UNSET:
            field_dict["@type"] = type
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
        from ..models.location_jsonld_contact_read_context_type_1 import LocationJsonldContactReadContextType1

        d = src_dict.copy()

        def _parse_context(data: object) -> Union["LocationJsonldContactReadContextType1", Unset, str]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                _context_type_1 = data
                context_type_1: Union[Unset, LocationJsonldContactReadContextType1]
                if isinstance(_context_type_1, Unset):
                    context_type_1 = UNSET
                else:
                    context_type_1 = LocationJsonldContactReadContextType1.from_dict(_context_type_1)

                return context_type_1
            except:  # noqa: E722
                pass
            return cast(Union["LocationJsonldContactReadContextType1", Unset, str], data)

        context = _parse_context(d.pop("@context", UNSET))

        id = d.pop("@id", UNSET)

        type = d.pop("@type", UNSET)

        city = d.pop("city", UNSET)

        postal_code = d.pop("postal_code", UNSET)

        timezone = d.pop("timezone", UNSET)

        lat = d.pop("lat", UNSET)

        lng = d.pop("lng", UNSET)

        country_code = d.pop("country_code", UNSET)

        country = d.pop("country", UNSET)

        location_jsonld_contact_read = cls(
            context=context,
            id=id,
            type=type,
            city=city,
            postal_code=postal_code,
            timezone=timezone,
            lat=lat,
            lng=lng,
            country_code=country_code,
            country=country,
        )

        location_jsonld_contact_read.additional_properties = d
        return location_jsonld_contact_read

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
