import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

import attr
from dateutil.parser import isoparse

from ..models.suscriber_source import SuscriberSource
from ..models.suscriber_status import SuscriberStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.group_jsonld_suscription_read import GroupJsonldSuscriptionRead
    from ..models.suscription_jsonld_suscription_read_context_type_1 import SuscriptionJsonldSuscriptionReadContextType1


T = TypeVar("T", bound="SuscriptionJsonldSuscriptionRead")


@attr.s(auto_attribs=True)
class SuscriptionJsonldSuscriptionRead:
    """
    Attributes:
        audience (str): Audience Example: /templates/0df14405-90ff-4287-b3e4-ef088901ee6f.
        id (Union[Unset, str]):
        type (Union[Unset, str]):
        context (Union['SuscriptionJsonldSuscriptionReadContextType1', Unset, str]):
        status (Union[Unset, SuscriberStatus]): Suscriber status:
            * `suscriber.status.confirmed` - Confirmed and active
            * `suscriber.status.unsuscribed` - Unsubscribed by contact
            * `suscriber.status.unsuscribed.admin` - Unsubscribed by admin
        source (Union[Unset, SuscriberSource]): Suscriber source:
            * `suscriber.source.manual` - Manually added by an admin
            * `suscriber.source.api` - Added through the API
            * `suscriber.source.webform` - Added from a webform
            * `suscriber.source.imported` - Added from an excel or csv importation
        rating (Union[Unset, None, float]): Engage rating (0 to 20) Example: 5.5.
        created_at (Union[Unset, None, datetime.datetime]): Date & Time resource created
        updated_at (Union[Unset, None, datetime.datetime]): Date & Time resource updated
        groups (Union[Unset, List['GroupJsonldSuscriptionRead']]):
        suscriber_consent (Union[Unset, None, str]):
        custom_fields (Union[Unset, List[str]]):
    """

    audience: str
    id: Union[Unset, str] = UNSET
    type: Union[Unset, str] = UNSET
    context: Union["SuscriptionJsonldSuscriptionReadContextType1", Unset, str] = UNSET
    status: Union[Unset, SuscriberStatus] = UNSET
    source: Union[Unset, SuscriberSource] = UNSET
    rating: Union[Unset, None, float] = UNSET
    created_at: Union[Unset, None, datetime.datetime] = UNSET
    updated_at: Union[Unset, None, datetime.datetime] = UNSET
    groups: Union[Unset, List["GroupJsonldSuscriptionRead"]] = UNSET
    suscriber_consent: Union[Unset, None, str] = UNSET
    custom_fields: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.suscription_jsonld_suscription_read_context_type_1 import (
            SuscriptionJsonldSuscriptionReadContextType1,
        )

        audience = self.audience
        id = self.id
        type = self.type
        context: Union[Dict[str, Any], Unset, str]
        if isinstance(self.context, Unset):
            context = UNSET

        elif isinstance(self.context, SuscriptionJsonldSuscriptionReadContextType1):
            context = UNSET
            if not isinstance(self.context, Unset):
                context = self.context.to_dict()

        else:
            context = self.context

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        source: Union[Unset, str] = UNSET
        if not isinstance(self.source, Unset):
            source = self.source.value

        rating = self.rating
        created_at: Union[Unset, None, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat() if self.created_at else None

        updated_at: Union[Unset, None, str] = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat() if self.updated_at else None

        groups: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.groups, Unset):
            groups = []
            for groups_item_data in self.groups:
                groups_item = groups_item_data.to_dict()

                groups.append(groups_item)

        suscriber_consent = self.suscriber_consent
        custom_fields: Union[Unset, List[str]] = UNSET
        if not isinstance(self.custom_fields, Unset):
            custom_fields = self.custom_fields

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "audience": audience,
            }
        )
        if id is not UNSET:
            field_dict["@id"] = id
        if type is not UNSET:
            field_dict["@type"] = type
        if context is not UNSET:
            field_dict["@context"] = context
        if status is not UNSET:
            field_dict["status"] = status
        if source is not UNSET:
            field_dict["source"] = source
        if rating is not UNSET:
            field_dict["rating"] = rating
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at
        if groups is not UNSET:
            field_dict["groups"] = groups
        if suscriber_consent is not UNSET:
            field_dict["suscriber_consent"] = suscriber_consent
        if custom_fields is not UNSET:
            field_dict["custom_fields"] = custom_fields

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.group_jsonld_suscription_read import GroupJsonldSuscriptionRead
        from ..models.suscription_jsonld_suscription_read_context_type_1 import (
            SuscriptionJsonldSuscriptionReadContextType1,
        )

        d = src_dict.copy()
        audience = d.pop("audience")

        id = d.pop("@id", UNSET)

        type = d.pop("@type", UNSET)

        def _parse_context(data: object) -> Union["SuscriptionJsonldSuscriptionReadContextType1", Unset, str]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                _context_type_1 = data
                context_type_1: Union[Unset, SuscriptionJsonldSuscriptionReadContextType1]
                if isinstance(_context_type_1, Unset):
                    context_type_1 = UNSET
                else:
                    context_type_1 = SuscriptionJsonldSuscriptionReadContextType1.from_dict(_context_type_1)

                return context_type_1
            except:  # noqa: E722
                pass
            return cast(Union["SuscriptionJsonldSuscriptionReadContextType1", Unset, str], data)

        context = _parse_context(d.pop("@context", UNSET))

        _status = d.pop("status", UNSET)
        status: Union[Unset, SuscriberStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = SuscriberStatus(_status)

        _source = d.pop("source", UNSET)
        source: Union[Unset, SuscriberSource]
        if isinstance(_source, Unset):
            source = UNSET
        else:
            source = SuscriberSource(_source)

        rating = d.pop("rating", UNSET)

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

        groups = []
        _groups = d.pop("groups", UNSET)
        for groups_item_data in _groups or []:
            groups_item = GroupJsonldSuscriptionRead.from_dict(groups_item_data)

            groups.append(groups_item)

        suscriber_consent = d.pop("suscriber_consent", UNSET)

        custom_fields = cast(List[str], d.pop("custom_fields", UNSET))

        suscription_jsonld_suscription_read = cls(
            audience=audience,
            id=id,
            type=type,
            context=context,
            status=status,
            source=source,
            rating=rating,
            created_at=created_at,
            updated_at=updated_at,
            groups=groups,
            suscriber_consent=suscriber_consent,
            custom_fields=custom_fields,
        )

        suscription_jsonld_suscription_read.additional_properties = d
        return suscription_jsonld_suscription_read

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
