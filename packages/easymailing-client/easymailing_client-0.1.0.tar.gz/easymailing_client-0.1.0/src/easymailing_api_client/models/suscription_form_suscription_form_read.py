import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..models.suscription_form_type import SuscriptionFormType
from ..types import UNSET, Unset

T = TypeVar("T", bound="SuscriptionFormSuscriptionFormRead")


@attr.s(auto_attribs=True)
class SuscriptionFormSuscriptionFormRead:
    """
    Attributes:
        hash_ (Union[Unset, str]): Hash to show in api Example: 7L4Gfr51podURoCdplgSKx.
        url (Union[Unset, str]): Url to show in api Example: https://myform.
        domain (Union[Unset, str]): Domain to show in api Example: mycompany.easymailing.com.
        title (Union[Unset, None, str]): Title Example: My awesome form.
        type (Union[Unset, SuscriptionFormType]): Form types:
            * `popup` - Popup
            * `embedded` - Embedded
        double_opt_in (Union[Unset, None, bool]): Is double opt-in? Example: True.
        enable_welcome_email (Union[Unset, None, bool]): Is welcome email enabled? Example: True.
        active (Union[Unset, None, bool]): Is active? Example: True.
        paused (Union[Unset, None, bool]): Is paused? Example: True.
        audience (Union[Unset, str]): Audience Example: /templates/0df14405-90ff-4287-b3e4-ef088901ee6f.
        created_at (Union[Unset, None, datetime.datetime]): Date & Time resource created
        updated_at (Union[Unset, None, datetime.datetime]): Date & Time resource updated
    """

    hash_: Union[Unset, str] = UNSET
    url: Union[Unset, str] = UNSET
    domain: Union[Unset, str] = UNSET
    title: Union[Unset, None, str] = UNSET
    type: Union[Unset, SuscriptionFormType] = UNSET
    double_opt_in: Union[Unset, None, bool] = UNSET
    enable_welcome_email: Union[Unset, None, bool] = UNSET
    active: Union[Unset, None, bool] = UNSET
    paused: Union[Unset, None, bool] = UNSET
    audience: Union[Unset, str] = UNSET
    created_at: Union[Unset, None, datetime.datetime] = UNSET
    updated_at: Union[Unset, None, datetime.datetime] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        hash_ = self.hash_
        url = self.url
        domain = self.domain
        title = self.title
        type: Union[Unset, str] = UNSET
        if not isinstance(self.type, Unset):
            type = self.type.value

        double_opt_in = self.double_opt_in
        enable_welcome_email = self.enable_welcome_email
        active = self.active
        paused = self.paused
        audience = self.audience
        created_at: Union[Unset, None, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat() if self.created_at else None

        updated_at: Union[Unset, None, str] = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat() if self.updated_at else None

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if hash_ is not UNSET:
            field_dict["hash"] = hash_
        if url is not UNSET:
            field_dict["url"] = url
        if domain is not UNSET:
            field_dict["domain"] = domain
        if title is not UNSET:
            field_dict["title"] = title
        if type is not UNSET:
            field_dict["type"] = type
        if double_opt_in is not UNSET:
            field_dict["double_opt_in"] = double_opt_in
        if enable_welcome_email is not UNSET:
            field_dict["enable_welcome_email"] = enable_welcome_email
        if active is not UNSET:
            field_dict["active"] = active
        if paused is not UNSET:
            field_dict["paused"] = paused
        if audience is not UNSET:
            field_dict["audience"] = audience
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        hash_ = d.pop("hash", UNSET)

        url = d.pop("url", UNSET)

        domain = d.pop("domain", UNSET)

        title = d.pop("title", UNSET)

        _type = d.pop("type", UNSET)
        type: Union[Unset, SuscriptionFormType]
        if isinstance(_type, Unset):
            type = UNSET
        else:
            type = SuscriptionFormType(_type)

        double_opt_in = d.pop("double_opt_in", UNSET)

        enable_welcome_email = d.pop("enable_welcome_email", UNSET)

        active = d.pop("active", UNSET)

        paused = d.pop("paused", UNSET)

        audience = d.pop("audience", UNSET)

        _created_at = d.pop("created_at", UNSET)
        created_at: Union[Unset, None, datetime.datetime]
        if _created_at is None:
            created_at = None
        elif isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        _updated_at = d.pop("updated_at", UNSET)
        updated_at: Union[Unset, None, datetime.datetime]
        if _updated_at is None:
            updated_at = None
        elif isinstance(_updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = isoparse(_updated_at)

        suscription_form_suscription_form_read = cls(
            hash_=hash_,
            url=url,
            domain=domain,
            title=title,
            type=type,
            double_opt_in=double_opt_in,
            enable_welcome_email=enable_welcome_email,
            active=active,
            paused=paused,
            audience=audience,
            created_at=created_at,
            updated_at=updated_at,
        )

        suscription_form_suscription_form_read.additional_properties = d
        return suscription_form_suscription_form_read

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
