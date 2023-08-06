from typing import Any, Dict, List, Type, TypeVar

import attr

T = TypeVar("T", bound="BlogImageResponseModel")


@attr.s(auto_attribs=True)
class BlogImageResponseModel:
    """Response model for an image derived from the blog's media.

    Attributes:
        timestamp (float):
        image_url (str):
        image_bucket (str):
        image_key (str):
    """

    timestamp: float
    image_url: str
    image_bucket: str
    image_key: str
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        timestamp = self.timestamp
        image_url = self.image_url
        image_bucket = self.image_bucket
        image_key = self.image_key

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "timestamp": timestamp,
                "image_url": image_url,
                "image_bucket": image_bucket,
                "image_key": image_key,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        timestamp = d.pop("timestamp")

        image_url = d.pop("image_url")

        image_bucket = d.pop("image_bucket")

        image_key = d.pop("image_key")

        blog_image_response_model = cls(
            timestamp=timestamp,
            image_url=image_url,
            image_bucket=image_bucket,
            image_key=image_key,
        )

        blog_image_response_model.additional_properties = d
        return blog_image_response_model

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
