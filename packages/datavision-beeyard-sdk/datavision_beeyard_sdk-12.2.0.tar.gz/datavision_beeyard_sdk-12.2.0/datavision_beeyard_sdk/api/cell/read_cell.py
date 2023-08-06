from ...client import AuthenticatedClient
import json


def read(id: str, *, client: AuthenticatedClient):
    url = "{}/api/v1/cells/{id}".format(client.base_url, id=id)
    response = client.get(url, headers=client.token_headers)
    return json.loads(response.content.decode("utf-8"))
