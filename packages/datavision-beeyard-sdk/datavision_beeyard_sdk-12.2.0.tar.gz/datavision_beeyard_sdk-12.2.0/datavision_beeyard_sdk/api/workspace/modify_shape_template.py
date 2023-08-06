from ...client import AuthenticatedClient


def update(
    workspace_id: str,
    *,
    client: AuthenticatedClient,
    shape_template_name: str,
    json_body: str
):
    url = (
        "{}/api/v1/workspaces/{workspaceId}/shapeTemplates/{shapeTemplateName}".format(
            client.base_url,
            workspaceId=workspace_id,
            shapeTemplateName=shape_template_name,
        )
    )
    header = {k: v for k, v in client.token_headers.items()}
    header["Content-Type"] = "application/json"
    response = client.patch(url, headers=header, data=json_body)
    return response
