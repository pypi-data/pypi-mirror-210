from ...client import AuthenticatedClient


def delete(workspace_id: str, *, client: AuthenticatedClient):
    url = "{}/api/v1/workspaces/{workspaceId}".format(
        client.base_url, workspaceId=workspace_id
    )
    response = client.delete(url, headers=client.token_headers)
    return response
