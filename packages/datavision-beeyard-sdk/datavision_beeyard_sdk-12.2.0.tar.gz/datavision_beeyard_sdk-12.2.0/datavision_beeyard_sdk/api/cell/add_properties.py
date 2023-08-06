import json
from ...client import AuthenticatedClient
from ...models.property_dto import PropertyDto


def add(id: str, *, client: AuthenticatedClient, props_list: [PropertyDto]):
    url = "{}/api/v1/cells/{id}/properties".format(client.base_url, id=id)
    header = {k: v for k, v in client.token_headers.items()}
    header["Content-Type"] = "application/json"
    props = [i.to_dict() for i in props_list]
    request_body = json.dumps(props)
    response = client.post(url, headers=header, data=request_body)
    return response
