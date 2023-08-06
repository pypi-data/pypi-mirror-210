from ...client import AuthenticatedClient


def query(*, client: AuthenticatedClient, accept: str = "application/json", query="[]"):
    url = "{}/api/v1/cells/aggregation".format(client.base_url)
    header = {k: v for k, v in client.token_headers.items()}
    header["accept"] = accept
    response = client.post(url, headers=header, data=query)
    return response.content
