from ...client import AuthenticatedClient


def read(id: str, overlay_name: str, shape_id: str, *, client: AuthenticatedClient):
    url = "{}/api/v1/cells/{id}/overlays/{overlayName}/shapes/{shapeId}".format(
        client.base_url, id=id, overlayName=overlay_name, shapeId=shape_id
    )
    response = client.get(url, headers=client.token_headers)
    return response.content
