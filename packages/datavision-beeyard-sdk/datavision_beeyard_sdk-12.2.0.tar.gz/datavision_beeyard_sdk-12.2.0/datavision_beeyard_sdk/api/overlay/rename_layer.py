from ...client import AuthenticatedClient


def update(
    id: str,
    client: AuthenticatedClient,
    *,
    overlay_name: str,
    layer_name: str,
    json_body: str
):
    url = "{}/api/v1/cells/{id}/overlays/{overlayName}/layers/{layerName}".format(
        client.base_url, id=id, overlayName=overlay_name, layerName=layer_name
    )
    header = {k: v for k, v in client.token_headers.items()}
    header["Content-Type"] = "application/json"
    response = client.patch(url, headers=header, data=json_body)
    return response
