from ...client import AuthenticatedClient


def delete(workspace_id: str, *, client: AuthenticatedClient, queries_list: [str]):
    url = "{}/api/v1/workspaces/{workspaceId}/favoriteQueries?queries=".format(
        client.base_url, workspaceId=workspace_id
    )
    tmp = "&queries="
    for q in queries_list:
        url = url + q + tmp
    response = client.delete(url[: -len(tmp)], headers=client.token_headers)
    return response
