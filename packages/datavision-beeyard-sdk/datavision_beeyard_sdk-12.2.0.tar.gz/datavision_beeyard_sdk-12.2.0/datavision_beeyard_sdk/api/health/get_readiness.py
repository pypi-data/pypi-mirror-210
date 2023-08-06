from ...client import AuthenticatedClient


def ready(*, client: AuthenticatedClient):
    url = "{}/api/v1/health/ready".format(client.base_url)
    response = client.get(url, headers=client.token_headers)
    return response.content
