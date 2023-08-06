from ...client import AuthenticatedClient


def version(*, client: AuthenticatedClient):
    url = "{}/api/v1/version".format(client.base_url)
    response = client.get(url, headers=client.token_headers)
    return response.content
