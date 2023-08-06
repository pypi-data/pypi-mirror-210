from ...client import AuthenticatedClient
from ...models.add_documents_multipart_data import AddDocumentsMultipartData


def add(
    id: str, *, client: AuthenticatedClient, multipart_data: AddDocumentsMultipartData
):
    url = "{}/api/v1/cells/{id}/overlays".format(client.base_url, id=id)
    request_body = multipart_data.to_multipart()
    response = client.post(url, headers=client.token_headers, files=request_body)
    return response
