import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="AutomationQueueAutomationQueueRead")


@attr.s(auto_attribs=True)
class AutomationQueueAutomationQueueRead:
    """
    Attributes:
        automation_trigger (Union[Unset, None, str]):
        suscription (Union[Unset, None, str]):
        created_at (Union[Unset, None, datetime.datetime]):
        updated_at (Union[Unset, None, datetime.datetime]):
    """

    automation_trigger: Union[Unset, None, str] = UNSET
    suscription: Union[Unset, None, str] = UNSET
    created_at: Union[Unset, None, datetime.datetime] = UNSET
    updated_at: Union[Unset, None, datetime.datetime] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        automation_trigger = self.automation_trigger
        suscription = self.suscription
        created_at: Union[Unset, None, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat() if self.created_at else None

        updated_at: Union[Unset, None, str] = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat() if self.updated_at else None

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if automation_trigger is not UNSET:
            field_dict["automation_trigger"] = automation_trigger
        if suscription is not UNSET:
            field_dict["suscription"] = suscription
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        automation_trigger = d.pop("automation_trigger", UNSET)

        suscription = d.pop("suscription", UNSET)

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

        automation_queue_automation_queue_read = cls(
            automation_trigger=automation_trigger,
            suscription=suscription,
            created_at=created_at,
            updated_at=updated_at,
        )

        automation_queue_automation_queue_read.additional_properties = d
        return automation_queue_automation_queue_read

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
