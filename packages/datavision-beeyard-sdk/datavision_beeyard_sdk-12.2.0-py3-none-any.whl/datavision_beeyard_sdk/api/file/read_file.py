from ...client import AuthenticatedClient


def read(id: str, filename: str, *, client: AuthenticatedClient):
    url = "{}/api/v1/cells/{id}/files/{filename}".format(
        client.base_url, id=id, filename=filename
    )
    response = client.get(url, headers=client.token_headers)
    return response.content
