from ...client import AuthenticatedClient
from ...models.favorite_query_dto import FavoriteQueryDto
import json


def add(
    workspace_id: str, *, client: AuthenticatedClient, query_to_add: [FavoriteQueryDto]
):
    url = "{}/api/v1/workspaces/{workspaceId}/favoriteQueries".format(
        client.base_url, workspaceId=workspace_id
    )
    header = {k: v for k, v in client.token_headers.items()}
    header["Content-Type"] = "application/json"
    qta = [q.to_dict() for q in query_to_add]
    json_qta = json.dumps(qta)
    response = client.post(url, headers=header, data=json_qta)
    return response
