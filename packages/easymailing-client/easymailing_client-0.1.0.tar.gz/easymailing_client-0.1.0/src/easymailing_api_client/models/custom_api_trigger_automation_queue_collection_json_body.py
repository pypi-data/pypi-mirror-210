from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="CustomApiTriggerAutomationQueueCollectionJsonBody")


@attr.s(auto_attribs=True)
class CustomApiTriggerAutomationQueueCollectionJsonBody:
    """
    Attributes:
        email (Union[Unset, str]): A suscriber email Example: user@company.com.
        automation_trigger (Union[Unset, str]): AutomationTrigger Example:
            /automation_triggers/0df14405-90ff-4287-b3e4-ef088901ee6f.
    """

    email: Union[Unset, str] = UNSET
    automation_trigger: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        email = self.email
        automation_trigger = self.automation_trigger

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if email is not UNSET:
            field_dict["email"] = email
        if automation_trigger is not UNSET:
            field_dict["automationTrigger"] = automation_trigger

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        email = d.pop("email", UNSET)

        automation_trigger = d.pop("automationTrigger", UNSET)

        custom_api_trigger_automation_queue_collection_json_body = cls(
            email=email,
            automation_trigger=automation_trigger,
        )

        custom_api_trigger_automation_queue_collection_json_body.additional_properties = d
        return custom_api_trigger_automation_queue_collection_json_body

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
