from ...client import AuthenticatedClient
from ...models.upload_mask_multipart_data import UploadMaskMultipartData


def upload(
    id: str,
    overlay_name: str,
    layer_name: str,
    *,
    client: AuthenticatedClient,
    mask_data: UploadMaskMultipartData
):
    url = "{}/api/v1/cells/{id}/overlays/{overlayName}/layers/{layerName}/masks/upload".format(
        client.base_url, id=id, overlayName=overlay_name, layerName=layer_name
    )
    multipart_data = mask_data.to_multipart()
    response = client.post(url, headers=client.token_headers, files=multipart_data)
    return response
