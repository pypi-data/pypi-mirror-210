from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.consent_contact_write import ConsentContactWrite
    from ..models.custom_field_contact_write import CustomFieldContactWrite


T = TypeVar("T", bound="ContactContactInputContactWrite")


@attr.s(auto_attribs=True)
class ContactContactInputContactWrite:
    """
    Attributes:
        email (Union[Unset, str]): Suscriber email
        audience (Union[Unset, str]): Audience Example: /audiences/0df14405-90ff-4287-b3e4-ef088901ee6f.
        groups (Union[Unset, List[str]]): The groups that are associated with a contact
        consent (Union[Unset, ConsentContactWrite]):
        client_ip (Union[Unset, None, str]): The client ip address the contact signup from Example: 10.0.0.1.
        locale (Union[Unset, None, str]): The client locale (ISO 3166-1 alpha-2) Example: es_ES.
        disable_double_opt_in (Union[Unset, bool]): Disable double opt-in for this suscription
        custom_fields (Union[Unset, List['CustomFieldContactWrite']]):
    """

    email: Union[Unset, str] = UNSET
    audience: Union[Unset, str] = UNSET
    groups: Union[Unset, List[str]] = UNSET
    consent: Union[Unset, "ConsentContactWrite"] = UNSET
    client_ip: Union[Unset, None, str] = UNSET
    locale: Union[Unset, None, str] = UNSET
    disable_double_opt_in: Union[Unset, bool] = UNSET
    custom_fields: Union[Unset, List["CustomFieldContactWrite"]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        email = self.email
        audience = self.audience
        groups: Union[Unset, List[str]] = UNSET
        if not isinstance(self.groups, Unset):
            groups = self.groups

        consent: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.consent, Unset):
            consent = self.consent.to_dict()

        client_ip = self.client_ip
        locale = self.locale
        disable_double_opt_in = self.disable_double_opt_in
        custom_fields: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.custom_fields, Unset):
            custom_fields = []
            for custom_fields_item_data in self.custom_fields:
                custom_fields_item = custom_fields_item_data.to_dict()

                custom_fields.append(custom_fields_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if email is not UNSET:
            field_dict["email"] = email
        if audience is not UNSET:
            field_dict["audience"] = audience
        if groups is not UNSET:
            field_dict["groups"] = groups
        if consent is not UNSET:
            field_dict["consent"] = consent
        if client_ip is not UNSET:
            field_dict["client_ip"] = client_ip
        if locale is not UNSET:
            field_dict["locale"] = locale
        if disable_double_opt_in is not UNSET:
            field_dict["disable_double_opt_in"] = disable_double_opt_in
        if custom_fields is not UNSET:
            field_dict["custom_fields"] = custom_fields

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.consent_contact_write import ConsentContactWrite
        from ..models.custom_field_contact_write import CustomFieldContactWrite

        d = src_dict.copy()
        email = d.pop("email", UNSET)

        audience = d.pop("audience", UNSET)

        groups = cast(List[str], d.pop("groups", UNSET))

        _consent = d.pop("consent", UNSET)
        consent: Union[Unset, ConsentContactWrite]
        if isinstance(_consent, Unset):
            consent = UNSET
        else:
            consent = ConsentContactWrite.from_dict(_consent)

        client_ip = d.pop("client_ip", UNSET)

        locale = d.pop("locale", UNSET)

        disable_double_opt_in = d.pop("disable_double_opt_in", UNSET)

        custom_fields = []
        _custom_fields = d.pop("custom_fields", UNSET)
        for custom_fields_item_data in _custom_fields or []:
            custom_fields_item = CustomFieldContactWrite.from_dict(custom_fields_item_data)

            custom_fields.append(custom_fields_item)

        contact_contact_input_contact_write = cls(
            email=email,
            audience=audience,
            groups=groups,
            consent=consent,
            client_ip=client_ip,
            locale=locale,
            disable_double_opt_in=disable_double_opt_in,
            custom_fields=custom_fields,
        )

        contact_contact_input_contact_write.additional_properties = d
        return contact_contact_input_contact_write

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
