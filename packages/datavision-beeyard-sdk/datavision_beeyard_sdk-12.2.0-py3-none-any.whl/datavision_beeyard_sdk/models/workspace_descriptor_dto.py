from typing import Any, Dict, Union
import attr
from ..types import UNSET, Unset


@attr.s(auto_attribs=True)
class WorkspaceDescriptorDto:
    """ """

    workspace_id: Union[Unset, str] = UNSET
    name: Union[Unset, None, str] = UNSET
    namespace: Union[Unset, None, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        workspace_id = self.workspace_id
        name = self.name
        namespace = self.namespace

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if workspace_id is not UNSET:
            field_dict["workspaceId"] = workspace_id
        if name is not UNSET:
            field_dict["name"] = name
        if namespace is not UNSET:
            field_dict["namespace"] = namespace
        return field_dict
