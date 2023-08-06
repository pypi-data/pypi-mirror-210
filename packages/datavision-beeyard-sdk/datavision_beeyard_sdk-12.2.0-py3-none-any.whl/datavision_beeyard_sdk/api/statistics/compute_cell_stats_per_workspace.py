from ...client import AuthenticatedClient
import json


def cell_count(
    workspace_id: str,
    *,
    client: AuthenticatedClient,
    accept: str = "application/json",
    query=""
):
    url = "{}/api/v1/workspaces/{workspaceId}/cells/stats".format(
        client.base_url, workspaceId=workspace_id
    )
    header = {k: v for k, v in client.token_headers.items()}
    header["accept"] = accept
    response = client.post(url, headers=header, data=query)
    return json.loads(response.content.decode("utf-8"))
