import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

import attr
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.sender_jsonld_sender_read_campaign_read_context_type_1 import (
        SenderJsonldSenderReadCampaignReadContextType1,
    )


T = TypeVar("T", bound="SenderJsonldSenderReadCampaignRead")


@attr.s(auto_attribs=True)
class SenderJsonldSenderReadCampaignRead:
    """
    Attributes:
        context (Union['SenderJsonldSenderReadCampaignReadContextType1', Unset, str]):
        id (Union[Unset, str]):
        type (Union[Unset, str]):
        email (Union[Unset, None, str]): The email to confirm Example: user@company.com.
        confirmed (Union[Unset, None, bool]): If it is confirmed to use in campaigns Example: True.
        created_at (Union[Unset, None, datetime.datetime]): Date & Time resource created
        updated_at (Union[Unset, None, datetime.datetime]): Date & Time resource updated
    """

    context: Union["SenderJsonldSenderReadCampaignReadContextType1", Unset, str] = UNSET
    id: Union[Unset, str] = UNSET
    type: Union[Unset, str] = UNSET
    email: Union[Unset, None, str] = UNSET
    confirmed: Union[Unset, None, bool] = UNSET
    created_at: Union[Unset, None, datetime.datetime] = UNSET
    updated_at: Union[Unset, None, datetime.datetime] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.sender_jsonld_sender_read_campaign_read_context_type_1 import (
            SenderJsonldSenderReadCampaignReadContextType1,
        )

        context: Union[Dict[str, Any], Unset, str]
        if isinstance(self.context, Unset):
            context = UNSET

        elif isinstance(self.context, SenderJsonldSenderReadCampaignReadContextType1):
            context = UNSET
            if not isinstance(self.context, Unset):
                context = self.context.to_dict()

        else:
            context = self.context

        id = self.id
        type = self.type
        email = self.email
        confirmed = self.confirmed
        created_at: Union[Unset, None, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat() if self.created_at else None

        updated_at: Union[Unset, None, str] = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat() if self.updated_at else None

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
        if confirmed is not UNSET:
            field_dict["confirmed"] = confirmed
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.sender_jsonld_sender_read_campaign_read_context_type_1 import (
            SenderJsonldSenderReadCampaignReadContextType1,
        )

        d = src_dict.copy()

        def _parse_context(data: object) -> Union["SenderJsonldSenderReadCampaignReadContextType1", Unset, str]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                _context_type_1 = data
                context_type_1: Union[Unset, SenderJsonldSenderReadCampaignReadContextType1]
                if isinstance(_context_type_1, Unset):
                    context_type_1 = UNSET
                else:
                    context_type_1 = SenderJsonldSenderReadCampaignReadContextType1.from_dict(_context_type_1)

                return context_type_1
            except:  # noqa: E722
                pass
            return cast(Union["SenderJsonldSenderReadCampaignReadContextType1", Unset, str], data)

        context = _parse_context(d.pop("@context", UNSET))

        id = d.pop("@id", UNSET)

        type = d.pop("@type", UNSET)

        email = d.pop("email", UNSET)

        confirmed = d.pop("confirmed", UNSET)

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

        sender_jsonld_sender_read_campaign_read = cls(
            context=context,
            id=id,
            type=type,
            email=email,
            confirmed=confirmed,
            created_at=created_at,
            updated_at=updated_at,
        )

        sender_jsonld_sender_read_campaign_read.additional_properties = d
        return sender_jsonld_sender_read_campaign_read

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
