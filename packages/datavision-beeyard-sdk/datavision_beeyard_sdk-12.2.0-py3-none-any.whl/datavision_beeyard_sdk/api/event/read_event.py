from ...client import AuthenticatedClient


def read(*, client: AuthenticatedClient, event_id: str):
    url = "{}/api/v1/events/{eventId}".format(client.base_url, eventId=event_id)
    response = client.get(url, headers=client.token_headers)
    return response.content
