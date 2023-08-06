from typing import Any, Dict, List, Union
import attr
from ..types import UNSET, File, FileJsonType, Unset


@attr.s(auto_attribs=True)
class AddImagesMultipartData:
    """ """

    files: Union[Unset, List[File]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        files: Union[Unset, List[FileJsonType]] = UNSET
        if not isinstance(self.files, Unset):
            files = []
            for files_item_data in self.files:
                files_item = files_item_data.to_tuple()

                files.append(files_item)
        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if files is not UNSET:
            field_dict["files"] = files
        return field_dict

    def to_multipart(self) -> Dict[str, Any]:
        if len(self.files) == 1:
            field_dict: Dict[str, Any] = {}
            field_dict["files"] = self.files[0].to_tuple()
            return field_dict
        else:
            files_list = []
            for item in self.files:
                files_item = item.to_tuple()
                files_list.append(("files", files_item))
            return files_list
