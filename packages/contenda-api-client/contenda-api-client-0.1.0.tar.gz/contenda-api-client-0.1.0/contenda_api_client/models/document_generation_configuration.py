from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.segment_configuration import SegmentConfiguration


T = TypeVar("T", bound="DocumentGenerationConfiguration")


@attr.s(auto_attribs=True)
class DocumentGenerationConfiguration:
    """Class for configuring blog document generation.

    Attributes:
        body_segment (Union[Unset, SegmentConfiguration]): Class for configuring blog segment generation.
        heading_segment (Union[Unset, SegmentConfiguration]): Class for configuring blog segment generation.
        question_segment (Union[Unset, SegmentConfiguration]): Class for configuring blog segment generation.
    """

    body_segment: Union[Unset, "SegmentConfiguration"] = UNSET
    heading_segment: Union[Unset, "SegmentConfiguration"] = UNSET
    question_segment: Union[Unset, "SegmentConfiguration"] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        body_segment: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.body_segment, Unset):
            body_segment = self.body_segment.to_dict()

        heading_segment: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.heading_segment, Unset):
            heading_segment = self.heading_segment.to_dict()

        question_segment: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.question_segment, Unset):
            question_segment = self.question_segment.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if body_segment is not UNSET:
            field_dict["body_segment"] = body_segment
        if heading_segment is not UNSET:
            field_dict["heading_segment"] = heading_segment
        if question_segment is not UNSET:
            field_dict["question_segment"] = question_segment

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.segment_configuration import SegmentConfiguration

        d = src_dict.copy()
        _body_segment = d.pop("body_segment", UNSET)
        body_segment: Union[Unset, SegmentConfiguration]
        if isinstance(_body_segment, Unset):
            body_segment = UNSET
        else:
            body_segment = SegmentConfiguration.from_dict(_body_segment)

        _heading_segment = d.pop("heading_segment", UNSET)
        heading_segment: Union[Unset, SegmentConfiguration]
        if isinstance(_heading_segment, Unset):
            heading_segment = UNSET
        else:
            heading_segment = SegmentConfiguration.from_dict(_heading_segment)

        _question_segment = d.pop("question_segment", UNSET)
        question_segment: Union[Unset, SegmentConfiguration]
        if isinstance(_question_segment, Unset):
            question_segment = UNSET
        else:
            question_segment = SegmentConfiguration.from_dict(_question_segment)

        document_generation_configuration = cls(
            body_segment=body_segment,
            heading_segment=heading_segment,
            question_segment=question_segment,
        )

        document_generation_configuration.additional_properties = d
        return document_generation_configuration

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
