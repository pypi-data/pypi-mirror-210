from ...client import AuthenticatedClient


def live(*, client: AuthenticatedClient):
    url = "{}/api/v1/health/live".format(client.base_url)
    response = client.get(url, headers=client.token_headers)
    return response.headers
