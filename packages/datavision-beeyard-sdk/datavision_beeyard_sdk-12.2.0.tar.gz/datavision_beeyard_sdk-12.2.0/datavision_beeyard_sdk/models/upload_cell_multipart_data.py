from typing import Any, Dict
import attr
from ..types import File


@attr.s(auto_attribs=True)
class UploadCellMultipartData:
    """ """

    files: [File]

    def to_dict(self) -> Dict[str, Any]:
        file_dict = {}
        for f in self.files:
            file_dict.update({f.file_name: f.payload})
        return file_dict
