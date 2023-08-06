from ...client import AuthenticatedClient
from ...models.add_images_multipart_data import AddImagesMultipartData


def upload(
    id: str,
    *,
    client: AuthenticatedClient,
    image_name: str,
    multipart_data: AddImagesMultipartData
):
    url = "{}/api/v1/cells/{id}/images/{imageName}/thumbnail".format(
        client.base_url, id=id, imageName=image_name
    )
    request_body = multipart_data.to_multipart()
    response = client.post(url, headers=client.token_headers, files=request_body)
    return response
