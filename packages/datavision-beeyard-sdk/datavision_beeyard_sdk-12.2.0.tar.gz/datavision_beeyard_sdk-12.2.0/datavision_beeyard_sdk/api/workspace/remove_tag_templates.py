from ...client import AuthenticatedClient
from ...models.tag_template_dto import TagTemplateDto
import json


def delete(
    workspace_id: str, *, client: AuthenticatedClient, tag_list: [TagTemplateDto]
):
    url = "{}/api/v1/workspaces/{workspaceId}/removeTagTemplates".format(
        client.base_url, workspaceId=workspace_id
    )
    header = {k: v for k, v in client.token_headers.items()}
    header["Content-Type"] = "application/json"
    tag_list = [t.to_dict() for t in tag_list]
    request_body = json.dumps(tag_list)
    response = client.post(url, headers=header, data=request_body)
    return response
