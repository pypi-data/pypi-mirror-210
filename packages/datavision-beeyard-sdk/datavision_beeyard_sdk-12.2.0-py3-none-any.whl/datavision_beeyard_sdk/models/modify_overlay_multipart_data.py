import attr
from typing import Any, Dict


@attr.s(auto_attribs=True)
class ModifyOverlayMultipartData:
    """ """

    shapesToModify: list
    shapesToRemove: list
    shapesToAdd: list

    def to_dict(self) -> Dict[str, Any]:
        field_dict = {}
        field_dict["shapesToModify"] = self.shapesToModify
        field_dict["shapesToRemove"] = self.shapesToRemove
        field_dict["shapesToAdd"] = self.shapesToAdd
        return field_dict
