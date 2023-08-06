from ...client import AuthenticatedClient
from ...models.favorite_query_dto import FavoriteQueryDto
import json


def replace(
    workspace_id: str, *, client: AuthenticatedClient, query_update: FavoriteQueryDto
):
    url = "{}/api/v1/workspaces/{workspaceId}/favoriteQueries".format(
        client.base_url, workspaceId=workspace_id
    )
    header = {k: v for k, v in client.token_headers.items()}
    header["Content-Type"] = "application/json"
    json_qta = json.dumps(query_update.to_dict())
    response = client.put(url, headers=header, data=json_qta)
    return response
