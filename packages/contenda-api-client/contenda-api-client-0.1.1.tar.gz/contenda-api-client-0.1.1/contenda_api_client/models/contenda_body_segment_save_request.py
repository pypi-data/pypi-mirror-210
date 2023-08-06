from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.blog_segment_type import BlogSegmentType
from ..types import UNSET, Unset

T = TypeVar("T", bound="ContendaBodySegmentSaveRequest")


@attr.s(auto_attribs=True)
class ContendaBodySegmentSaveRequest:
    """Request model for a generated segment type BODY.

    Attributes:
        id (str):
        text (str):
        active_revision_id (str):
        segment_type (Union[Unset, BlogSegmentType]): Enumerable for the different types a BlogSegment can have.
            Default: BlogSegmentType.BODY.
    """

    id: str
    text: str
    active_revision_id: str
    segment_type: Union[Unset, BlogSegmentType] = BlogSegmentType.BODY
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        text = self.text
        active_revision_id = self.active_revision_id
        segment_type: Union[Unset, str] = UNSET
        if not isinstance(self.segment_type, Unset):
            segment_type = self.segment_type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "text": text,
                "active_revision_id": active_revision_id,
            }
        )
        if segment_type is not UNSET:
            field_dict["segment_type"] = segment_type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        text = d.pop("text")

        active_revision_id = d.pop("active_revision_id")

        _segment_type = d.pop("segment_type", UNSET)
        segment_type: Union[Unset, BlogSegmentType]
        if isinstance(_segment_type, Unset):
            segment_type = UNSET
        else:
            segment_type = BlogSegmentType(_segment_type)

        contenda_body_segment_save_request = cls(
            id=id,
            text=text,
            active_revision_id=active_revision_id,
            segment_type=segment_type,
        )

        contenda_body_segment_save_request.additional_properties = d
        return contenda_body_segment_save_request

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
