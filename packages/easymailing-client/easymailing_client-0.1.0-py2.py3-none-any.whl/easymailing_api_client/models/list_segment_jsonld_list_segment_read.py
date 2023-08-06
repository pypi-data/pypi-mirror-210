import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Type, TypeVar, Union, cast

import attr
from dateutil.parser import isoparse

from ..models.list_segment_operator_match import ListSegmentOperatorMatch
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.list_segment_jsonld_list_segment_read_context_type_1 import (
        ListSegmentJsonldListSegmentReadContextType1,
    )


T = TypeVar("T", bound="ListSegmentJsonldListSegmentRead")


@attr.s(auto_attribs=True)
class ListSegmentJsonldListSegmentRead:
    """
    Attributes:
        operator_match (ListSegmentOperatorMatch): Operator match:
            * `any` - Match any conditions
            * `all` - Match all conditions
        id (Union[Unset, str]):
        type (Union[Unset, str]):
        context (Union['ListSegmentJsonldListSegmentReadContextType1', Unset, str]):
        name (Optional[datetime.datetime]): Segment name Example: My awesome segmentation!.
        description (Union[Unset, None, str]): Segment description Example: Custom segmentation description.
        suscriber_count (Union[Unset, None, int]): Total suscribers on updated date Example: 1500.
        audience (Union[Unset, None, str]): Audience Example: /audiences/0df14405-90ff-4287-b3e4-ef088901ee6f.
        created_at (Union[Unset, None, datetime.datetime]): Date & Time resource created
        updated_at (Union[Unset, None, datetime.datetime]): Date & Time resource updated
    """

    operator_match: ListSegmentOperatorMatch
    name: Optional[datetime.datetime]
    id: Union[Unset, str] = UNSET
    type: Union[Unset, str] = UNSET
    context: Union["ListSegmentJsonldListSegmentReadContextType1", Unset, str] = UNSET
    description: Union[Unset, None, str] = UNSET
    suscriber_count: Union[Unset, None, int] = UNSET
    audience: Union[Unset, None, str] = UNSET
    created_at: Union[Unset, None, datetime.datetime] = UNSET
    updated_at: Union[Unset, None, datetime.datetime] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.list_segment_jsonld_list_segment_read_context_type_1 import (
            ListSegmentJsonldListSegmentReadContextType1,
        )

        operator_match = self.operator_match.value

        id = self.id
        type = self.type
        context: Union[Dict[str, Any], Unset, str]
        if isinstance(self.context, Unset):
            context = UNSET

        elif isinstance(self.context, ListSegmentJsonldListSegmentReadContextType1):
            context = UNSET
            if not isinstance(self.context, Unset):
                context = self.context.to_dict()

        else:
            context = self.context

        name = self.name.isoformat() if self.name else None

        description = self.description
        suscriber_count = self.suscriber_count
        audience = self.audience
        created_at: Union[Unset, None, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat() if self.created_at else None

        updated_at: Union[Unset, None, str] = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat() if self.updated_at else None

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "operator_match": operator_match,
                "name": name,
            }
        )
        if id is not UNSET:
            field_dict["@id"] = id
        if type is not UNSET:
            field_dict["@type"] = type
        if context is not UNSET:
            field_dict["@context"] = context
        if description is not UNSET:
            field_dict["description"] = description
        if suscriber_count is not UNSET:
            field_dict["suscriber_count"] = suscriber_count
        if audience is not UNSET:
            field_dict["audience"] = audience
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.list_segment_jsonld_list_segment_read_context_type_1 import (
            ListSegmentJsonldListSegmentReadContextType1,
        )

        d = src_dict.copy()
        operator_match = ListSegmentOperatorMatch(d.pop("operator_match"))

        id = d.pop("@id", UNSET)

        type = d.pop("@type", UNSET)

        def _parse_context(data: object) -> Union["ListSegmentJsonldListSegmentReadContextType1", Unset, str]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                _context_type_1 = data
                context_type_1: Union[Unset, ListSegmentJsonldListSegmentReadContextType1]
                if isinstance(_context_type_1, Unset):
                    context_type_1 = UNSET
                else:
                    context_type_1 = ListSegmentJsonldListSegmentReadContextType1.from_dict(_context_type_1)

                return context_type_1
            except:  # noqa: E722
                pass
            return cast(Union["ListSegmentJsonldListSegmentReadContextType1", Unset, str], data)

        context = _parse_context(d.pop("@context", UNSET))

        _name = d.pop("name")
        name: Optional[datetime.datetime]
        if _name is None:
            name = None
        else:
            name = isoparse(_name)

        description = d.pop("description", UNSET)

        suscriber_count = d.pop("suscriber_count", UNSET)

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

        list_segment_jsonld_list_segment_read = cls(
            operator_match=operator_match,
            id=id,
            type=type,
            context=context,
            name=name,
            description=description,
            suscriber_count=suscriber_count,
            audience=audience,
            created_at=created_at,
            updated_at=updated_at,
        )

        list_segment_jsonld_list_segment_read.additional_properties = d
        return list_segment_jsonld_list_segment_read

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
