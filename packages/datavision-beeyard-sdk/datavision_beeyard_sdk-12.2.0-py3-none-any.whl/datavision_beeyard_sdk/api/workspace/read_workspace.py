from ...client import AuthenticatedClient


def read(workspace_id: str, *, client: AuthenticatedClient):
    url = "{}/api/v1/workspaces/{workspaceId}".format(
        client.base_url, workspaceId=workspace_id
    )
    response = client.get(url, headers=client.token_headers)
    return response.content
