from ...client import AuthenticatedClient
from ...models.reference_dto import ReferenceDto
import json


def add(id: str, *, client: AuthenticatedClient, ref_list: [ReferenceDto]):
    url = "{}/api/v1/cells/{id}/references".format(client.base_url, id=id)
    header = {k: v for k, v in client.token_headers.items()}
    header["Content-Type"] = "application/json"
    refs = [i.to_dict() for i in ref_list]
    request_body = json.dumps(refs)
    response = client.post(url, headers=header, data=request_body)
    return response
