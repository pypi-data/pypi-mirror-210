from typing import Any, Dict, List, Type, TypeVar

import attr

T = TypeVar("T", bound="TranscriptLineResponseModel")


@attr.s(auto_attribs=True)
class TranscriptLineResponseModel:
    """Response model for a line in the transcript.

    Attributes:
        start_time (float):
        end_time (float):
        text (str):
    """

    start_time: float
    end_time: float
    text: str
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        start_time = self.start_time
        end_time = self.end_time
        text = self.text

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "start_time": start_time,
                "end_time": end_time,
                "text": text,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        start_time = d.pop("start_time")

        end_time = d.pop("end_time")

        text = d.pop("text")

        transcript_line_response_model = cls(
            start_time=start_time,
            end_time=end_time,
            text=text,
        )

        transcript_line_response_model.additional_properties = d
        return transcript_line_response_model

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
