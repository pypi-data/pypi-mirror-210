from typing import Any, Dict, List, TypeVar, Union
import attr
from ..models.tag_dto import TagDto
from ..types import UNSET, Unset

T = TypeVar("T", bound="UpdateTagsDto")


@attr.s(auto_attribs=True)
class UpdateTagsDto:
    """ """

    to_add: Union[Unset, None, List[TagDto]] = UNSET
    to_remove: Union[Unset, None, List[TagDto]] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        to_add = self.to_add
        to_remove = self.to_remove
        add_tags = []
        for item in self.to_add:
            item_to_add = item.to_dict()
            add_tags.append(item_to_add)
        remove_tags = []
        for item in self.to_remove:
            item_to_remove = item.to_dict()
            remove_tags.append(item_to_remove)
        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if to_add is not UNSET:
            field_dict["toAdd"] = add_tags
        if to_remove is not UNSET:
            field_dict["toRemove"] = remove_tags

        return field_dict
