from ...client import AuthenticatedClient


def remove(id: str, *, client: AuthenticatedClient, filenames: [str]):
    url = "{}/api/v1/cells/{id}/files?filenames=".format(client.base_url, id=id)
    for f in filenames:
        url = url + f + "&filenames="
    response = client.delete(url[:-11], headers=client.token_headers)
    return response
