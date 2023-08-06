from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.automation_automation_trigger_read import AutomationAutomationTriggerRead


T = TypeVar("T", bound="AutomationTriggerAutomationTriggerRead")


@attr.s(auto_attribs=True)
class AutomationTriggerAutomationTriggerRead:
    """
    Attributes:
        trigger_type (Union[Unset, None, str]):
        automation (Union[Unset, None, AutomationAutomationTriggerRead]):
    """

    trigger_type: Union[Unset, None, str] = UNSET
    automation: Union[Unset, None, "AutomationAutomationTriggerRead"] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        trigger_type = self.trigger_type
        automation: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.automation, Unset):
            automation = self.automation.to_dict() if self.automation else None

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if trigger_type is not UNSET:
            field_dict["trigger_type"] = trigger_type
        if automation is not UNSET:
            field_dict["automation"] = automation

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.automation_automation_trigger_read import AutomationAutomationTriggerRead

        d = src_dict.copy()
        trigger_type = d.pop("trigger_type", UNSET)

        _automation = d.pop("automation", UNSET)
        automation: Union[Unset, None, AutomationAutomationTriggerRead]
        if _automation is None:
            automation = None
        elif isinstance(_automation, Unset):
            automation = UNSET
        else:
            automation = AutomationAutomationTriggerRead.from_dict(_automation)

        automation_trigger_automation_trigger_read = cls(
            trigger_type=trigger_type,
            automation=automation,
        )

        automation_trigger_automation_trigger_read.additional_properties = d
        return automation_trigger_automation_trigger_read

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
