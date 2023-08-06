import datetime
from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="BlogEntry")


@attr.s(auto_attribs=True)
class BlogEntry:
    """Blog entry response model.

    Attributes:
        id (str):
        title (str):
        owner_email (str):
        owner_name (str):
        created_at (datetime.datetime):
        labels (Union[Unset, List[str]]):
    """

    id: str
    title: str
    owner_email: str
    owner_name: str
    created_at: datetime.datetime
    labels: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        title = self.title
        owner_email = self.owner_email
        owner_name = self.owner_name
        created_at = self.created_at.isoformat()

        labels: Union[Unset, List[str]] = UNSET
        if not isinstance(self.labels, Unset):
            labels = self.labels

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "title": title,
                "owner_email": owner_email,
                "owner_name": owner_name,
                "created_at": created_at,
            }
        )
        if labels is not UNSET:
            field_dict["labels"] = labels

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        title = d.pop("title")

        owner_email = d.pop("owner_email")

        owner_name = d.pop("owner_name")

        created_at = isoparse(d.pop("created_at"))

        labels = cast(List[str], d.pop("labels", UNSET))

        blog_entry = cls(
            id=id,
            title=title,
            owner_email=owner_email,
            owner_name=owner_name,
            created_at=created_at,
            labels=labels,
        )

        blog_entry.additional_properties = d
        return blog_entry

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
