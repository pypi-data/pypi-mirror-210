from typing import TYPE_CHECKING, Any, Dict, List, Optional, Type, TypeVar, Union, cast

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.data_manager_jsonld_audience_read_context_type_1 import DataManagerJsonldAudienceReadContextType1


T = TypeVar("T", bound="DataManagerJsonldAudienceRead")


@attr.s(auto_attribs=True)
class DataManagerJsonldAudienceRead:
    """
    Attributes:
        context (Union['DataManagerJsonldAudienceReadContextType1', Unset, str]):
        id (Union[Unset, str]):
        type (Union[Unset, str]):
        name (Optional[str]): Firstname and lastname or Company name
        identification_number (Optional[str]): Identification number ID / VAT ID
        phone (Union[Unset, None, str]): Phone number
        website (Union[Unset, None, str]): Website url
        email (Optional[str]): Email
        address (Optional[str]): Address
        postal_code (Optional[str]): Postal code
        city (Optional[str]): City
        province (Optional[str]): Province
        country (Optional[str]): Country
    """

    name: Optional[str]
    identification_number: Optional[str]
    email: Optional[str]
    address: Optional[str]
    postal_code: Optional[str]
    city: Optional[str]
    province: Optional[str]
    country: Optional[str]
    context: Union["DataManagerJsonldAudienceReadContextType1", Unset, str] = UNSET
    id: Union[Unset, str] = UNSET
    type: Union[Unset, str] = UNSET
    phone: Union[Unset, None, str] = UNSET
    website: Union[Unset, None, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.data_manager_jsonld_audience_read_context_type_1 import DataManagerJsonldAudienceReadContextType1

        context: Union[Dict[str, Any], Unset, str]
        if isinstance(self.context, Unset):
            context = UNSET

        elif isinstance(self.context, DataManagerJsonldAudienceReadContextType1):
            context = UNSET
            if not isinstance(self.context, Unset):
                context = self.context.to_dict()

        else:
            context = self.context

        id = self.id
        type = self.type
        name = self.name
        identification_number = self.identification_number
        phone = self.phone
        website = self.website
        email = self.email
        address = self.address
        postal_code = self.postal_code
        city = self.city
        province = self.province
        country = self.country

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "identification_number": identification_number,
                "email": email,
                "address": address,
                "postal_code": postal_code,
                "city": city,
                "province": province,
                "country": country,
            }
        )
        if context is not UNSET:
            field_dict["@context"] = context
        if id is not UNSET:
            field_dict["@id"] = id
        if type is not UNSET:
            field_dict["@type"] = type
        if phone is not UNSET:
            field_dict["phone"] = phone
        if website is not UNSET:
            field_dict["website"] = website

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.data_manager_jsonld_audience_read_context_type_1 import DataManagerJsonldAudienceReadContextType1

        d = src_dict.copy()

        def _parse_context(data: object) -> Union["DataManagerJsonldAudienceReadContextType1", Unset, str]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                _context_type_1 = data
                context_type_1: Union[Unset, DataManagerJsonldAudienceReadContextType1]
                if isinstance(_context_type_1, Unset):
                    context_type_1 = UNSET
                else:
                    context_type_1 = DataManagerJsonldAudienceReadContextType1.from_dict(_context_type_1)

                return context_type_1
            except:  # noqa: E722
                pass
            return cast(Union["DataManagerJsonldAudienceReadContextType1", Unset, str], data)

        context = _parse_context(d.pop("@context", UNSET))

        id = d.pop("@id", UNSET)

        type = d.pop("@type", UNSET)

        name = d.pop("name")

        identification_number = d.pop("identification_number")

        phone = d.pop("phone", UNSET)

        website = d.pop("website", UNSET)

        email = d.pop("email")

        address = d.pop("address")

        postal_code = d.pop("postal_code")

        city = d.pop("city")

        province = d.pop("province")

        country = d.pop("country")

        data_manager_jsonld_audience_read = cls(
            context=context,
            id=id,
            type=type,
            name=name,
            identification_number=identification_number,
            phone=phone,
            website=website,
            email=email,
            address=address,
            postal_code=postal_code,
            city=city,
            province=province,
            country=country,
        )

        data_manager_jsonld_audience_read.additional_properties = d
        return data_manager_jsonld_audience_read

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
