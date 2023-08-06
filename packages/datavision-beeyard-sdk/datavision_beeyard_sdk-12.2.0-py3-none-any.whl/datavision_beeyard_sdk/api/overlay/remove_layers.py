from ...client import AuthenticatedClient


def remove(
    id: str, overlay_name: str, *, client: AuthenticatedClient, layer_names: [str]
):
    url = "{}/api/v1/cells/{id}/overlays/{overlayName}/layers?layerNames=".format(
        client.base_url, id=id, overlayName=overlay_name
    )
    for layer in layer_names:
        url = url + layer + "&layerNames="
    response = client.delete(url[:-12], headers=client.token_headers)
    return response
