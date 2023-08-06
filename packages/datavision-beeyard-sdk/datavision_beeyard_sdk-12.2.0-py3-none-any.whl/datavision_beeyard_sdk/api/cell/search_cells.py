import json
from ...client import AuthenticatedClient


def query(
    *,
    client: AuthenticatedClient,
    query="",
    sort_by="created",
    sort_direction="desc",
    namespace="",
    page_index=0,
    page_size=100
):
    url = "{}/api/v1/cells/search".format(client.base_url)
    url_with_param = (
        url
        + "?sortBy="
        + sort_by
        + "&sortDirection="
        + sort_direction
        + "&namespace="
        + namespace
        + "&pageIndex="
        + str(page_index)
        + "&pageSize="
        + str(page_size)
    )
    response = client.post(url_with_param, headers=client.token_headers, data=query)
    return json.loads(response.content.decode("utf-8"))
