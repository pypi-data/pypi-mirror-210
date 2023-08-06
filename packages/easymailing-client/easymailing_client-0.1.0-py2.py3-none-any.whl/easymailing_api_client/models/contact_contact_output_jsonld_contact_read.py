import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

import attr
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.contact_contact_output_jsonld_contact_read_context_type_1 import (
        ContactContactOutputJsonldContactReadContextType1,
    )
    from ..models.location_jsonld_contact_read import LocationJsonldContactRead
    from ..models.suscription_jsonld_contact_read import SuscriptionJsonldContactRead


T = TypeVar("T", bound="ContactContactOutputJsonldContactRead")


@attr.s(auto_attribs=True)
class ContactContactOutputJsonldContactRead:
    """
    Attributes:
        context (Union['ContactContactOutputJsonldContactReadContextType1', Unset, str]):
        id (Union[Unset, str]):
        type (Union[Unset, str]):
        email (Union[Unset, str]): Suscriber email Example: name@company.com.
        location (Union[Unset, LocationJsonldContactRead]):
        suscriptions (Union[Unset, List['SuscriptionJsonldContactRead']]):
        created_at (Union[Unset, datetime.datetime]): Created Datetime Example: 2020-01-01T00:00:00+00:00.
        updated_at (Union[Unset, datetime.datetime]): Updated Datetime Example: 2020-01-01T00:00:00+00:00.
        client_ip (Union[Unset, None, str]): The client ip address the contact signup from Example: 10.0.0.1.
        locale (Union[Unset, None, str]): The client locale (ISO 3166-1 alpha-2) Example: es_ES.
    """

    context: Union["ContactContactOutputJsonldContactReadContextType1", Unset, str] = UNSET
    id: Union[Unset, str] = UNSET
    type: Union[Unset, str] = UNSET
    email: Union[Unset, str] = UNSET
    location: Union[Unset, "LocationJsonldContactRead"] = UNSET
    suscriptions: Union[Unset, List["SuscriptionJsonldContactRead"]] = UNSET
    created_at: Union[Unset, datetime.datetime] = UNSET
    updated_at: Union[Unset, datetime.datetime] = UNSET
    client_ip: Union[Unset, None, str] = UNSET
    locale: Union[Unset, None, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.contact_contact_output_jsonld_contact_read_context_type_1 import (
            ContactContactOutputJsonldContactReadContextType1,
        )

        context: Union[Dict[str, Any], Unset, str]
        if isinstance(self.context, Unset):
            context = UNSET

        elif isinstance(self.context, ContactContactOutputJsonldContactReadContextType1):
            context = UNSET
            if not isinstance(self.context, Unset):
                context = self.context.to_dict()

        else:
            context = self.context

        id = self.id
        type = self.type
        email = self.email
        location: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.location, Unset):
            location = self.location.to_dict()

        suscriptions: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.suscriptions, Unset):
            suscriptions = []
            for suscriptions_item_data in self.suscriptions:
                suscriptions_item = suscriptions_item_data.to_dict()

                suscriptions.append(suscriptions_item)

        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        updated_at: Union[Unset, str] = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat()

        client_ip = self.client_ip
        locale = self.locale

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if context is not UNSET:
            field_dict["@context"] = context
        if id is not UNSET:
            field_dict["@id"] = id
        if type is not UNSET:
            field_dict["@type"] = type
        if email is not UNSET:
            field_dict["email"] = email
        if location is not UNSET:
            field_dict["location"] = location
        if suscriptions is not UNSET:
            field_dict["suscriptions"] = suscriptions
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at
        if client_ip is not UNSET:
            field_dict["client_ip"] = client_ip
        if locale is not UNSET:
            field_dict["locale"] = locale

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.contact_contact_output_jsonld_contact_read_context_type_1 import (
            ContactContactOutputJsonldContactReadContextType1,
        )
        from ..models.location_jsonld_contact_read import LocationJsonldContactRead
        from ..models.suscription_jsonld_contact_read import SuscriptionJsonldContactRead

        d = src_dict.copy()

        def _parse_context(data: object) -> Union["ContactContactOutputJsonldContactReadContextType1", Unset, str]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                _context_type_1 = data
                context_type_1: Union[Unset, ContactContactOutputJsonldContactReadContextType1]
                if isinstance(_context_type_1, Unset):
                    context_type_1 = UNSET
                else:
                    context_type_1 = ContactContactOutputJsonldContactReadContextType1.from_dict(_context_type_1)

                return context_type_1
            except:  # noqa: E722
                pass
            return cast(Union["ContactContactOutputJsonldContactReadContextType1", Unset, str], data)

        context = _parse_context(d.pop("@context", UNSET))

        id = d.pop("@id", UNSET)

        type = d.pop("@type", UNSET)

        email = d.pop("email", UNSET)

        _location = d.pop("location", UNSET)
        location: Union[Unset, LocationJsonldContactRead]
        if isinstance(_location, Unset):
            location = UNSET
        else:
            location = LocationJsonldContactRead.from_dict(_location)

        suscriptions = []
        _suscriptions = d.pop("suscriptions", UNSET)
        for suscriptions_item_data in _suscriptions or []:
            suscriptions_item = SuscriptionJsonldContactRead.from_dict(suscriptions_item_data)

            suscriptions.append(suscriptions_item)

        _created_at = d.pop("created_at", UNSET)
        created_at: Union[Unset, datetime.datetime]
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        _updated_at = d.pop("updated_at", UNSET)
        updated_at: Union[Unset, datetime.datetime]
        if isinstance(_updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = isoparse(_updated_at)

        client_ip = d.pop("client_ip", UNSET)

        locale = d.pop("locale", UNSET)

        contact_contact_output_jsonld_contact_read = cls(
            context=context,
            id=id,
            type=type,
            email=email,
            location=location,
            suscriptions=suscriptions,
            created_at=created_at,
            updated_at=updated_at,
            client_ip=client_ip,
            locale=locale,
        )

        contact_contact_output_jsonld_contact_read.additional_properties = d
        return contact_contact_output_jsonld_contact_read

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
