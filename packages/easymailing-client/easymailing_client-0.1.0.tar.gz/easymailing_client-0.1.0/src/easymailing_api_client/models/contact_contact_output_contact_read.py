import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.location_contact_read import LocationContactRead
    from ..models.suscription_contact_read import SuscriptionContactRead


T = TypeVar("T", bound="ContactContactOutputContactRead")


@attr.s(auto_attribs=True)
class ContactContactOutputContactRead:
    """
    Attributes:
        email (Union[Unset, str]): Suscriber email Example: name@company.com.
        location (Union[Unset, LocationContactRead]):
        suscriptions (Union[Unset, List['SuscriptionContactRead']]):
        created_at (Union[Unset, datetime.datetime]): Created Datetime Example: 2020-01-01T00:00:00+00:00.
        updated_at (Union[Unset, datetime.datetime]): Updated Datetime Example: 2020-01-01T00:00:00+00:00.
        client_ip (Union[Unset, None, str]): The client ip address the contact signup from Example: 10.0.0.1.
        locale (Union[Unset, None, str]): The client locale (ISO 3166-1 alpha-2) Example: es_ES.
    """

    email: Union[Unset, str] = UNSET
    location: Union[Unset, "LocationContactRead"] = UNSET
    suscriptions: Union[Unset, List["SuscriptionContactRead"]] = UNSET
    created_at: Union[Unset, datetime.datetime] = UNSET
    updated_at: Union[Unset, datetime.datetime] = UNSET
    client_ip: Union[Unset, None, str] = UNSET
    locale: Union[Unset, None, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
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
        from ..models.location_contact_read import LocationContactRead
        from ..models.suscription_contact_read import SuscriptionContactRead

        d = src_dict.copy()
        email = d.pop("email", UNSET)

        _location = d.pop("location", UNSET)
        location: Union[Unset, LocationContactRead]
        if isinstance(_location, Unset):
            location = UNSET
        else:
            location = LocationContactRead.from_dict(_location)

        suscriptions = []
        _suscriptions = d.pop("suscriptions", UNSET)
        for suscriptions_item_data in _suscriptions or []:
            suscriptions_item = SuscriptionContactRead.from_dict(suscriptions_item_data)

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

        contact_contact_output_contact_read = cls(
            email=email,
            location=location,
            suscriptions=suscriptions,
            created_at=created_at,
            updated_at=updated_at,
            client_ip=client_ip,
            locale=locale,
        )

        contact_contact_output_contact_read.additional_properties = d
        return contact_contact_output_contact_read

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
