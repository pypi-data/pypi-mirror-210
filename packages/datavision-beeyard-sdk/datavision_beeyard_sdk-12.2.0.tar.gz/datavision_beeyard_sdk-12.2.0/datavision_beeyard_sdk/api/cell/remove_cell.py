from ...client import AuthenticatedClient


def remove(id: str, *, client: AuthenticatedClient, namespace=None):
    url = "{}/api/v1/cells/{id}".format(client.base_url, id=id)
    response = client.delete(url, headers=client.token_headers)
    return response
