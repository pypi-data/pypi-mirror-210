from ...client import AuthenticatedClient


def update(workspace_id: str, *, client: AuthenticatedClient, json_body: str):
    url = "{}/api/v1/workspaces/{workspaceId}".format(
        client.base_url, workspaceId=workspace_id
    )
    header = {k: v for k, v in client.token_headers.items()}
    header["Content-Type"] = "application/json"
    response = client.patch(url, headers=header, data=json_body)
    return response
