from ...client import AuthenticatedClient


def read(id: str, *, client: AuthenticatedClient):
    url = "{}/api/v1/cells/{id}/overlays".format(client.base_url, id=id)
    response = client.get(url, headers=client.token_headers)
    return response.content
