from ...client import AuthenticatedClient


def delete(workspace_id: str, *, client: AuthenticatedClient, template_list: [str]):
    url = "{}/api/v1/workspaces/{workspaceId}/shapeTemplates?shapes=".format(
        client.base_url, workspaceId=workspace_id
    )
    for i in template_list:
        url = url + i + "&shapes="
    response = client.delete(url[:-8], headers=client.token_headers)
    return response
