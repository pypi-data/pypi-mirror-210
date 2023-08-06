from ...client import AuthenticatedClient


def remove(
    id: str, overlay_name: str, *, client: AuthenticatedClient, shape_ids: [str]
):
    url = "{}/api/v1/cells/{id}/overlays/{overlayName}?shapeIds=".format(
        client.base_url, id=id, overlayName=overlay_name
    )
    for i in shape_ids:
        url = url + i + "&shapeIds="
    response = client.delete(url[:-10], headers=client.token_headers)
    return response
