def create(client, namespace=None, additional_tags=None, additional_properties=None):
    if namespace is not None:
        url = client.base_url + "/api/v1/cells/new?namespace=" + namespace
        if additional_tags is not None:
            url = url + "&" + build_tail(additional_tags)
        if additional_properties is not None:
            url = url + "&" + build_tail(additional_properties)
    else:
        url = client.base_url + "/api/v1/cells/new"
        if additional_tags is not None:
            url = url + "?" + build_tail(additional_tags)
        if additional_properties is not None:
            url = url + "?" + build_tail(additional_properties)
    response = client.post(url, headers=client.token_headers)
    return response


def build_tail(arg):
    url_tail = ""
    for key in arg.keys():
        for prop in arg[key]:
            url_tail = url_tail + key + "=" + prop + "&"
    return url_tail[:-1]
