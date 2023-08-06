from typing import Any, Dict, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="TagDto")


@attr.s(auto_attribs=True)
class TagDto:
    """ """

    category: Union[Unset, None, str] = UNSET
    name: Union[Unset, None, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        category = self.category
        name = self.name

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if category is not UNSET:
            field_dict["category"] = category
        if name is not UNSET:
            field_dict["name"] = name
        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        category = d.pop("category", UNSET)

        name = d.pop("name", UNSET)

        tag_dto = cls(
            category=category,
            name=name,
        )

        return tag_dto
