from ...client import AuthenticatedClient
import json


def search(id: str, *, client: AuthenticatedClient):
    url = "{}/api/v1/cells/{id}/references/cells".format(client.base_url, id=id)
    response = client.get(url, headers=client.token_headers)
    return json.loads(response.content)
