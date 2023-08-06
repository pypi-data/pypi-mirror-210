from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..models.video_to_blog_type import VideoToBlogType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.document_generation_configuration import DocumentGenerationConfiguration


T = TypeVar("T", bound="JobCreateVideoToBlog")


@attr.s(auto_attribs=True)
class JobCreateVideoToBlog:
    """Video to blog job creation model.

    Attributes:
        type (VideoToBlogType): Input video types for the video to blog pipeline.
        status_update_webhook_url (Union[Unset, str]): This URL will be called with updated whenever the job updates.
            Default: ''.
        status_update_email (Union[Unset, str]): This address will sent an e-mail whenever the job updates. Defaults to
            the user creating the job. Default: ''.
        source_id (Union[Unset, str]): Source id for the media the job will process, e.g. youtube dQw4w9WgXcQ. Default:
            'youtube dQw4w9WgXcQ'.
        labels (Union[Unset, List[str]]): Arbitrary labels that may be passed through to job results.
        overrides (Union[Unset, DocumentGenerationConfiguration]): Class for configuring blog document generation.
    """

    type: VideoToBlogType
    status_update_webhook_url: Union[Unset, str] = ""
    status_update_email: Union[Unset, str] = ""
    source_id: Union[Unset, str] = "youtube dQw4w9WgXcQ"
    labels: Union[Unset, List[str]] = UNSET
    overrides: Union[Unset, "DocumentGenerationConfiguration"] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        type = self.type.value

        status_update_webhook_url = self.status_update_webhook_url
        status_update_email = self.status_update_email
        source_id = self.source_id
        labels: Union[Unset, List[str]] = UNSET
        if not isinstance(self.labels, Unset):
            labels = self.labels

        overrides: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.overrides, Unset):
            overrides = self.overrides.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type,
            }
        )
        if status_update_webhook_url is not UNSET:
            field_dict["status_update_webhook_url"] = status_update_webhook_url
        if status_update_email is not UNSET:
            field_dict["status_update_email"] = status_update_email
        if source_id is not UNSET:
            field_dict["source_id"] = source_id
        if labels is not UNSET:
            field_dict["labels"] = labels
        if overrides is not UNSET:
            field_dict["overrides"] = overrides

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.document_generation_configuration import DocumentGenerationConfiguration

        d = src_dict.copy()
        type = VideoToBlogType(d.pop("type"))

        status_update_webhook_url = d.pop("status_update_webhook_url", UNSET)

        status_update_email = d.pop("status_update_email", UNSET)

        source_id = d.pop("source_id", UNSET)

        labels = cast(List[str], d.pop("labels", UNSET))

        _overrides = d.pop("overrides", UNSET)
        overrides: Union[Unset, DocumentGenerationConfiguration]
        if isinstance(_overrides, Unset):
            overrides = UNSET
        else:
            overrides = DocumentGenerationConfiguration.from_dict(_overrides)

        job_create_video_to_blog = cls(
            type=type,
            status_update_webhook_url=status_update_webhook_url,
            status_update_email=status_update_email,
            source_id=source_id,
            labels=labels,
            overrides=overrides,
        )

        job_create_video_to_blog.additional_properties = d
        return job_create_video_to_blog

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
