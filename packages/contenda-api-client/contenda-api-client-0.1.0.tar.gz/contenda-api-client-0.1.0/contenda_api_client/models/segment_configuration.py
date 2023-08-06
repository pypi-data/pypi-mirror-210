from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.regeneration_fn_name import RegenerationFnName
from ..types import UNSET, Unset

T = TypeVar("T", bound="SegmentConfiguration")


@attr.s(auto_attribs=True)
class SegmentConfiguration:
    """Class for configuring blog segment generation.

    Attributes:
        prompt_template_name (Union[Unset, str]):
        prompt_template_string (Union[Unset, str]):
        system_message_name (Union[Unset, str]):
        system_message_string (Union[Unset, str]):
        completion_max_tokens (Union[Unset, int]):
        temperature (Union[Unset, float]):
        regeneration_fn (Union[Unset, RegenerationFnName]): Enumerable for regeneration functions.
        regeneration_tries (Union[Unset, int]):
        regeneration_threshold (Union[Unset, float]):
    """

    prompt_template_name: Union[Unset, str] = UNSET
    prompt_template_string: Union[Unset, str] = UNSET
    system_message_name: Union[Unset, str] = UNSET
    system_message_string: Union[Unset, str] = UNSET
    completion_max_tokens: Union[Unset, int] = UNSET
    temperature: Union[Unset, float] = UNSET
    regeneration_fn: Union[Unset, RegenerationFnName] = UNSET
    regeneration_tries: Union[Unset, int] = UNSET
    regeneration_threshold: Union[Unset, float] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        prompt_template_name = self.prompt_template_name
        prompt_template_string = self.prompt_template_string
        system_message_name = self.system_message_name
        system_message_string = self.system_message_string
        completion_max_tokens = self.completion_max_tokens
        temperature = self.temperature
        regeneration_fn: Union[Unset, str] = UNSET
        if not isinstance(self.regeneration_fn, Unset):
            regeneration_fn = self.regeneration_fn.value

        regeneration_tries = self.regeneration_tries
        regeneration_threshold = self.regeneration_threshold

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if prompt_template_name is not UNSET:
            field_dict["prompt_template_name"] = prompt_template_name
        if prompt_template_string is not UNSET:
            field_dict["prompt_template_string"] = prompt_template_string
        if system_message_name is not UNSET:
            field_dict["system_message_name"] = system_message_name
        if system_message_string is not UNSET:
            field_dict["system_message_string"] = system_message_string
        if completion_max_tokens is not UNSET:
            field_dict["completion_max_tokens"] = completion_max_tokens
        if temperature is not UNSET:
            field_dict["temperature"] = temperature
        if regeneration_fn is not UNSET:
            field_dict["regeneration_fn"] = regeneration_fn
        if regeneration_tries is not UNSET:
            field_dict["regeneration_tries"] = regeneration_tries
        if regeneration_threshold is not UNSET:
            field_dict["regeneration_threshold"] = regeneration_threshold

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        prompt_template_name = d.pop("prompt_template_name", UNSET)

        prompt_template_string = d.pop("prompt_template_string", UNSET)

        system_message_name = d.pop("system_message_name", UNSET)

        system_message_string = d.pop("system_message_string", UNSET)

        completion_max_tokens = d.pop("completion_max_tokens", UNSET)

        temperature = d.pop("temperature", UNSET)

        _regeneration_fn = d.pop("regeneration_fn", UNSET)
        regeneration_fn: Union[Unset, RegenerationFnName]
        if isinstance(_regeneration_fn, Unset):
            regeneration_fn = UNSET
        else:
            regeneration_fn = RegenerationFnName(_regeneration_fn)

        regeneration_tries = d.pop("regeneration_tries", UNSET)

        regeneration_threshold = d.pop("regeneration_threshold", UNSET)

        segment_configuration = cls(
            prompt_template_name=prompt_template_name,
            prompt_template_string=prompt_template_string,
            system_message_name=system_message_name,
            system_message_string=system_message_string,
            completion_max_tokens=completion_max_tokens,
            temperature=temperature,
            regeneration_fn=regeneration_fn,
            regeneration_tries=regeneration_tries,
            regeneration_threshold=regeneration_threshold,
        )

        segment_configuration.additional_properties = d
        return segment_configuration

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
