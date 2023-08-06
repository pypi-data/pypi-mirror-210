from typing import Any, Dict, List, Type, TypeVar

import attr

T = TypeVar(
    "T", bound="SaveBlogResultDocumentApiV2ContentBlogBlogIdPutResponseSaveBlogResultDocumentApiV2ContentBlogBlogIdPut"
)


@attr.s(auto_attribs=True)
class SaveBlogResultDocumentApiV2ContentBlogBlogIdPutResponseSaveBlogResultDocumentApiV2ContentBlogBlogIdPut:
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
        save_blog_result_document_api_v2_content_blog_blog_id_put_response_save_blog_result_document_api_v2_content_blog_blog_id_put = (
            cls()
        )

        save_blog_result_document_api_v2_content_blog_blog_id_put_response_save_blog_result_document_api_v2_content_blog_blog_id_put.additional_properties = (
            d
        )
        return save_blog_result_document_api_v2_content_blog_blog_id_put_response_save_blog_result_document_api_v2_content_blog_blog_id_put

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
