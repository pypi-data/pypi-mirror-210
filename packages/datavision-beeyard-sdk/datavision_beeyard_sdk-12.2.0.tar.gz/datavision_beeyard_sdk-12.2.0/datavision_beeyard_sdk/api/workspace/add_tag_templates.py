from typing import List
from ...client import AuthenticatedClient
from ...models.tag_template_dto import TagTemplateDto
import json


def add(
    workspace_id: str, *, client: AuthenticatedClient, tag_list: List[TagTemplateDto]
):
    url = "{}/api/v1/workspaces/{workspaceId}/addTagTemplates".format(
        client.base_url, workspaceId=workspace_id
    )
    template_list = []
    for json_body_item_data in tag_list:
        json_body_item = json_body_item_data.to_dict()
        template_list.append(json_body_item)
    header = {k: v for k, v in client.token_headers.items()}
    header["Content-Type"] = "application/json"
    request_body = json.dumps(template_list).encode()
    response = client.post(url, headers=header, data=request_body)
    return response
