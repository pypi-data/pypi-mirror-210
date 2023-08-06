from ...client import AuthenticatedClient


def update(*, id: str, client: AuthenticatedClient, filename: str, json_body: str):
    url = "{}/api/v1/cells/{id}/files/{filename}".format(
        client.base_url, id=id, filename=filename
    )
    header = {k: v for k, v in client.token_headers.items()}
    header["Content-Type"] = "application/json"
    response = client.patch(url, headers=header, data=json_body)
    return response
