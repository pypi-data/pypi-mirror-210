from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="GenerateAccessToken")


@attr.s(auto_attribs=True)
class GenerateAccessToken:
    """Generate access token model.

    Attributes:
        email (Union[Unset, str]): The e-mail address of the user. Default: ''.
        api_key (Union[Unset, str]): The API key of the user. Default: ''.
    """

    email: Union[Unset, str] = ""
    api_key: Union[Unset, str] = ""
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        email = self.email
        api_key = self.api_key

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if email is not UNSET:
            field_dict["email"] = email
        if api_key is not UNSET:
            field_dict["api_key"] = api_key

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        email = d.pop("email", UNSET)

        api_key = d.pop("api_key", UNSET)

        generate_access_token = cls(
            email=email,
            api_key=api_key,
        )

        generate_access_token.additional_properties = d
        return generate_access_token

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
