from typing import Any, Dict, List, Type, TypeVar

import attr

T = TypeVar(
    "T", bound="GetBlogResultDocumentApiV2ContentBlogBlogIdGetResponseGetBlogResultDocumentApiV2ContentBlogBlogIdGet"
)


@attr.s(auto_attribs=True)
class GetBlogResultDocumentApiV2ContentBlogBlogIdGetResponseGetBlogResultDocumentApiV2ContentBlogBlogIdGet:
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
        get_blog_result_document_api_v2_content_blog_blog_id_get_response_get_blog_result_document_api_v2_content_blog_blog_id_get = (
            cls()
        )

        get_blog_result_document_api_v2_content_blog_blog_id_get_response_get_blog_result_document_api_v2_content_blog_blog_id_get.additional_properties = (
            d
        )
        return get_blog_result_document_api_v2_content_blog_blog_id_get_response_get_blog_result_document_api_v2_content_blog_blog_id_get

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
