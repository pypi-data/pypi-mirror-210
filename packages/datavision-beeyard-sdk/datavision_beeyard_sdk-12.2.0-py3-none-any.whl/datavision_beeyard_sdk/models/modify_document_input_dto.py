from typing import Any, Dict, Type, TypeVar, Union
import attr
from ..types import UNSET, Unset

T = TypeVar("T", bound="ModifyDocumentInputDto")


@attr.s(auto_attribs=True)
class ModifyDocumentInputDto:
    """ """

    content: Union[Unset, Any] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        content = self.content

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if content is not UNSET:
            field_dict["content"] = content

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        content = d.pop("content", UNSET)

        modify_document_input_dto = cls(
            content=content,
        )

        return modify_document_input_dto
