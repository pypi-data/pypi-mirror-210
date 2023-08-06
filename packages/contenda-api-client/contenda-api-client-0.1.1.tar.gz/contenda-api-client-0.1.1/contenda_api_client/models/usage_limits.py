from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="UsageLimits")


@attr.s(auto_attribs=True)
class UsageLimits:
    """Usage limits response model.

    Attributes:
        is_unlimited (bool):
        friendly_message (str):
        period (Union[Unset, str]):
        limit (Union[Unset, float]):
        current (Union[Unset, float]):
    """

    is_unlimited: bool
    friendly_message: str
    period: Union[Unset, str] = UNSET
    limit: Union[Unset, float] = UNSET
    current: Union[Unset, float] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        is_unlimited = self.is_unlimited
        friendly_message = self.friendly_message
        period = self.period
        limit = self.limit
        current = self.current

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "is_unlimited": is_unlimited,
                "friendly_message": friendly_message,
            }
        )
        if period is not UNSET:
            field_dict["period"] = period
        if limit is not UNSET:
            field_dict["limit"] = limit
        if current is not UNSET:
            field_dict["current"] = current

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        is_unlimited = d.pop("is_unlimited")

        friendly_message = d.pop("friendly_message")

        period = d.pop("period", UNSET)

        limit = d.pop("limit", UNSET)

        current = d.pop("current", UNSET)

        usage_limits = cls(
            is_unlimited=is_unlimited,
            friendly_message=friendly_message,
            period=period,
            limit=limit,
            current=current,
        )

        usage_limits.additional_properties = d
        return usage_limits

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
