from ...client import AuthenticatedClient
import json


def add(
    id: str,
    overlay_name: str,
    layer_name: str,
    *,
    client: AuthenticatedClient,
    shape_list: []
):
    url = "{}/api/v1/cells/{id}/overlays/{overlayName}/layers/{layerName}".format(
        client.base_url, id=id, overlayName=overlay_name, layerName=layer_name
    )
    header = {k: v for k, v in client.token_headers.items()}
    header["Content-Type"] = "application/json"
    json_body = json.dumps(shape_list)
    response = client.post(url, headers=header, data=json_body)
    return response
