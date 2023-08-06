from ...client import AuthenticatedClient
from ...models.modify_overlay_multipart_data import ModifyOverlayMultipartData
import json


def update(
    *,
    id: str,
    client: AuthenticatedClient,
    overlay_name: str,
    shape_to_modify: ModifyOverlayMultipartData
):
    url = "{}/api/v1/cells/{id}/overlays/{overlayName}".format(
        client.base_url, id=id, overlayName=overlay_name
    )
    header = {k: v for k, v in client.token_headers.items()}
    header["Content-Type"] = "application/json"
    json_body = json.dumps(shape_to_modify.to_dict())
    response = client.patch(url, headers=header, data=json_body)
    return response
