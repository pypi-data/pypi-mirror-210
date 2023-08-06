from typing import Any, Dict, Union
import attr
from ..types import UNSET, Unset


@attr.s(auto_attribs=True)
class TagTemplateDto:
    """ """

    section: Union[Unset, None, str] = UNSET
    name: Union[Unset, None, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        section = self.section
        name = self.name

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if section is not UNSET:
            field_dict["section"] = section
        if name is not UNSET:
            field_dict["name"] = name

        return field_dict
