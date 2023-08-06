from ...client import AuthenticatedClient
from ...models.modify_cell_input_dto import ModifyCellInputDto


def update_description(
    id: str, *, client: AuthenticatedClient, description: ModifyCellInputDto
):
    url = "{}/api/v1/cells/{id}".format(client.base_url, id=id)
    request_body = description.to_dict()
    header = {k: v for k, v in client.token_headers.items()}
    header["Content-Type"] = "application/json"
    response = client.patch(url, headers=header, data=request_body)
    return response
