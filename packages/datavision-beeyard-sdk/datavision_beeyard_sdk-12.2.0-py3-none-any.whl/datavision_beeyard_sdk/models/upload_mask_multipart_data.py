from typing import Any, Dict, TypeVar
import attr
from ..types import File

T = TypeVar("T", bound="UploadMaskMultipartData")


@attr.s(auto_attribs=True)
class UploadMaskMultipartData:
    """ """

    mask: File
    image: File

    def to_dict(self) -> Dict[str, Any]:
        mask = self.mask.to_tuple()

        image = self.image.to_tuple()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "mask": mask,
                "image": image,
            }
        )

        return field_dict

    def to_multipart(self) -> Dict[str, Any]:
        mask = self.mask.to_tuple()

        image = self.image.to_tuple()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "mask": mask,
                "image": image,
            }
        )

        return field_dict
