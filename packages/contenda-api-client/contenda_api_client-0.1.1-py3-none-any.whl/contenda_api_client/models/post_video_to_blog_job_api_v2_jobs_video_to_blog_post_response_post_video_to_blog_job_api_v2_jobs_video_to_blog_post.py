from typing import Any, Dict, List, Type, TypeVar

import attr

T = TypeVar("T", bound="PostVideoToBlogJobApiV2JobsVideoToBlogPostResponsePostVideoToBlogJobApiV2JobsVideoToBlogPost")


@attr.s(auto_attribs=True)
class PostVideoToBlogJobApiV2JobsVideoToBlogPostResponsePostVideoToBlogJobApiV2JobsVideoToBlogPost:
    """ """

    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        post_video_to_blog_job_api_v2_jobs_video_to_blog_post_response_post_video_to_blog_job_api_v2_jobs_video_to_blog_post = (
            cls()
        )

        post_video_to_blog_job_api_v2_jobs_video_to_blog_post_response_post_video_to_blog_job_api_v2_jobs_video_to_blog_post.additional_properties = (
            d
        )
        return post_video_to_blog_job_api_v2_jobs_video_to_blog_post_response_post_video_to_blog_job_api_v2_jobs_video_to_blog_post

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
