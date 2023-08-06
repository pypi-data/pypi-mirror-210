from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.regeneration_label import RegenerationLabel
from ..types import UNSET, Unset

T = TypeVar("T", bound="SegmentRevisionFeedbackRequestModel")


@attr.s(auto_attribs=True)
class SegmentRevisionFeedbackRequestModel:
    """Response model for the body input of saving segment revisions after regeneration.

    Attributes:
        regeneration_reason (RegenerationLabel): Enumerable for labeling different reasons a segment was regenerated.
            The text values are also used by the frontend to display, retrieved via an endpoint
        regeneration_reason_options (Union[Unset, List[RegenerationLabel]]):
    """

    regeneration_reason: RegenerationLabel
    regeneration_reason_options: Union[Unset, List[RegenerationLabel]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        regeneration_reason = self.regeneration_reason.value

        regeneration_reason_options: Union[Unset, List[str]] = UNSET
        if not isinstance(self.regeneration_reason_options, Unset):
            regeneration_reason_options = []
            for regeneration_reason_options_item_data in self.regeneration_reason_options:
                regeneration_reason_options_item = regeneration_reason_options_item_data.value

                regeneration_reason_options.append(regeneration_reason_options_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "regeneration_reason": regeneration_reason,
            }
        )
        if regeneration_reason_options is not UNSET:
            field_dict["regeneration_reason_options"] = regeneration_reason_options

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        regeneration_reason = RegenerationLabel(d.pop("regeneration_reason"))

        regeneration_reason_options = []
        _regeneration_reason_options = d.pop("regeneration_reason_options", UNSET)
        for regeneration_reason_options_item_data in _regeneration_reason_options or []:
            regeneration_reason_options_item = RegenerationLabel(regeneration_reason_options_item_data)

            regeneration_reason_options.append(regeneration_reason_options_item)

        segment_revision_feedback_request_model = cls(
            regeneration_reason=regeneration_reason,
            regeneration_reason_options=regeneration_reason_options,
        )

        segment_revision_feedback_request_model.additional_properties = d
        return segment_revision_feedback_request_model

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
