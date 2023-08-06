from ...client import AuthenticatedClient
import json


def compute(workspace_id: str, *, client: AuthenticatedClient, query: str):
    url = "{}/api/v1/workspaces/{workspaceId}/tags/stats".format(
        client.base_url, workspaceId=workspace_id
    )
    response = client.post(url, headers=client.token_headers, data=query)
    return json.loads(response.content)
