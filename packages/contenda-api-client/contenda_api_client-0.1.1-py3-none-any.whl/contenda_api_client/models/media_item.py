import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="MediaItem")


@attr.s(auto_attribs=True)
class MediaItem:
    """Model for media items.

    Attributes:
        id (str):
        source_id (str):
        mime_type (str):
        owner_id (str):
        file_md5 (Union[Unset, str]):  Default: ''.
        length (Union[Unset, float]):
        title (Union[Unset, str]):  Default: ''.
        description (Union[Unset, str]):  Default: ''.
        created_at (Union[Unset, datetime.datetime]):
    """

    id: str
    source_id: str
    mime_type: str
    owner_id: str
    file_md5: Union[Unset, str] = ""
    length: Union[Unset, float] = 0.0
    title: Union[Unset, str] = ""
    description: Union[Unset, str] = ""
    created_at: Union[Unset, datetime.datetime] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        source_id = self.source_id
        mime_type = self.mime_type
        owner_id = self.owner_id
        file_md5 = self.file_md5
        length = self.length
        title = self.title
        description = self.description
        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "source_id": source_id,
                "mime_type": mime_type,
                "owner_id": owner_id,
            }
        )
        if file_md5 is not UNSET:
            field_dict["file_md5"] = file_md5
        if length is not UNSET:
            field_dict["length"] = length
        if title is not UNSET:
            field_dict["title"] = title
        if description is not UNSET:
            field_dict["description"] = description
        if created_at is not UNSET:
            field_dict["created_at"] = created_at

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        source_id = d.pop("source_id")

        mime_type = d.pop("mime_type")

        owner_id = d.pop("owner_id")

        file_md5 = d.pop("file_md5", UNSET)

        length = d.pop("length", UNSET)

        title = d.pop("title", UNSET)

        description = d.pop("description", UNSET)

        _created_at = d.pop("created_at", UNSET)
        created_at: Union[Unset, datetime.datetime]
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        media_item = cls(
            id=id,
            source_id=source_id,
            mime_type=mime_type,
            owner_id=owner_id,
            file_md5=file_md5,
            length=length,
            title=title,
            description=description,
            created_at=created_at,
        )

        media_item.additional_properties = d
        return media_item

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
